#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
=======================
Usage
=======================

Usage:
  jumeaux init
  jumeaux init <name>
  jumeaux run <files>... [--config=<yaml>...] [--title=<title>] [--description=<description>]
                         [--tag=<tag>...] [--skip-addon-tag=<skip_add_on_tag>...]
                         [--threads=<threads>] [--processes=<processes>]
                         [--max-retries=<max_retries>] [-vvv]
  jumeaux retry <report> [--title=<title>] [--description=<description>]
                         [--tag=<tag>...] [--threads=<threads>] [--processes=<processes>]
                         [--max-retries=<max_retries>] [-vvv]
  jumeaux server [--port=<port>]

Options:
  <name>                                        Initialize template name
  <files>...                                    Files written requests
  --config = <yaml>...                          Configuration files(see below) [def: config.yml]
  --title = <title>                             The title of report [def: No title]
  --description = <description>                 The description of report
  --tag = <tag>...                              Tags
  --skip-addon-tag = <skip_addon_tag>...        Skip add-ons loading whose tags have one of this
  --threads = <threads>                         The number of threads in challenge [def: 1]
  --processes = <processes>                     The number of processes in challenge
  --max-retries = <max_retries>                 The max number of retries which accesses to API
  <report>                                      Report for retry
  -vvv                                          Logger level (`-v` or `-vv` or `-vvv`)
  --port = <port>                               Running port [def: 8000]
"""

import hashlib
import io
import os
import shutil
import sys
import datetime
import http.server
import socketserver
import urllib.parse as urlparser
from concurrent import futures
from typing import Tuple, Optional, Any

import requests
from deepdiff import DeepDiff
from docopt import docopt
from fn import _
from owlmixin import TList, TOption, TDict
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(PROJECT_ROOT)
from jumeaux import __version__
from jumeaux.addons import AddOnExecutor
from jumeaux.configmaker import create_config, create_config_from_report
from jumeaux.models import (
    Config,
    Report,
    Request,
    Response,
    Args,
    ChallengeArg,
    Trial,
    Proxy,
    Summary,
    Concurrency,
    Log2ReqsAddOnPayload,
    Reqs2ReqsAddOnPayload,
    Res2ResAddOnPayload,
    Res2DictAddOnPayload,
    JudgementAddOnPayload,
    JudgementAddOnReference,
    StoreCriterionAddOnPayload,
    StoreCriterionAddOnReference,
    DumpAddOnPayload,
    FinalAddOnPayload,
    DidChallengeAddOnPayload,
    DiffKeys,
    Status,
)
from jumeaux.logger import Logger, init_logger

logger: Logger = Logger(__name__)
global_addon_executor: AddOnExecutor = None


def now():
    """
    For test
    """
    return datetime.datetime.today()


def write_to_file(name, dir, body):
    with open(f'{dir}/{name}', "bw") as f:
        f.write(body)


def make_dir(path):
    os.makedirs(path)
    os.chmod(path, 0o777)


def http_get(args: Tuple[Any, str, TDict[str], TDict[str]]):
    session, url, headers, proxies = args
    try:
        r = session.get(url, headers=headers.assign({'User-Agent': f'jumeaux/{__version__}'}), proxies=proxies)
    finally:
        session.close()
    return r


def to_sec(elapsed):
    return round(elapsed.seconds + elapsed.microseconds / 1000000, 2)


def concurrent_request(session, headers: TDict[str], url_one, url_other, proxies_one, proxies_other):
    fs = ((session, url_one, headers, proxies_one),
          (session, url_other, headers, proxies_other))
    with futures.ThreadPoolExecutor(max_workers=2) as ex:
        res_one, res_other = ex.map(http_get, fs)

    return res_one, res_other


def res2res(res: Response, req: Request):
    return global_addon_executor.apply_res2res(Res2ResAddOnPayload.from_dict({
        "response": res,
        "req": req,
    })).response


def res2dict(res: Response) -> TOption[dict]:
    return global_addon_executor.apply_res2dict(Res2DictAddOnPayload.from_dict({
        "response": res,
        "result": None
    })).result


def judgement(r_one: Response, r_other: Response,
              d_one: TOption[dict], d_other: TOption[dict],
              name: str, path: str, qs: TDict[TList[str]], headers: TList[str],
              diff_keys: Optional[DiffKeys]) -> Status:
    regard_as_same: bool = global_addon_executor.apply_judgement(
        JudgementAddOnPayload.from_dict({
            "remaining_diff_keys": diff_keys,
            "regard_as_same": r_one.body == r_other.body,
        }),
        JudgementAddOnReference.from_dict({
            "name": name,
            "path": path,
            "qs": qs,
            "headers": headers,
            "dict_one": d_one,
            "dict_other": d_other,
            "res_one": r_one,
            "res_other": r_other,
            "diff_keys": diff_keys,
        })
    ).regard_as_same
    return Status.SAME if regard_as_same else Status.DIFFERENT  # type: ignore # Prevent for enum problem


def store_criterion(status: Status, path: str, qs: TDict[TList[str]], headers: TDict[str],
                    r_one: Response, r_other: Response):
    return global_addon_executor.apply_store_criterion(
        StoreCriterionAddOnPayload.from_dict({
            "stored": False,
        }),
        StoreCriterionAddOnReference.from_dict({
            "status": status,
            "path": path,
            "qs": qs,
            "headers": headers,
            "res_one": r_one,
            "res_other": r_other,
        }),
    ).stored


def dump(res: Response):
    return global_addon_executor.apply_dump(DumpAddOnPayload.from_dict({
        "response": res,
        "body": res.body,
        "encoding": res.encoding
    })).body


def challenge(arg: ChallengeArg) -> dict:
    """ Response is dict like `Trial` because Status(OwlEnum) can't be pickled.
    """

    name: str = arg.req.name.get_or(str(arg.seq))
    log_prefix = f"[{arg.seq} / {arg.number_of_request}]"

    logger.info_lv3(f"{log_prefix} {'-'*80}")
    logger.info_lv3(f"{log_prefix}  {arg.seq}. {arg.req.name.get_or(arg.req.path)}")
    logger.info_lv3(f"{log_prefix} {'-'*80}")

    qs_str = urlparser.urlencode(arg.req.qs, doseq=True)

    url_one = f'{arg.host_one}{arg.req.path}?{qs_str}'
    url_other = f'{arg.host_other}{arg.req.path}?{qs_str}'

    # Get two responses
    req_time = now()
    try:
        logger.info_lv3(f"{log_prefix} One:   {url_one}")
        logger.info_lv3(f"{log_prefix} Other: {url_other}")
        r_one, r_other = concurrent_request(arg.session, arg.req.headers,
                                            url_one, url_other,
                                            arg.proxy_one.get(), arg.proxy_other.get())
        logger.info_lv3(
            f"{log_prefix} One:   {r_one.status_code} / {to_sec(r_one.elapsed)}s / {len(r_one.content)}b / {r_one.headers.get('content-type')}" # noqa
        )
        logger.info_lv3(
            f"{log_prefix} Other: {r_other.status_code} / {to_sec(r_other.elapsed)}s / {len(r_other.content)}b / {r_other.headers.get('content-type')}" # noqa
        )
    except ConnectionError:
        logger.info_lv1(f"{log_prefix} 💀 {arg.req.name.get()}")
        # TODO: Integrate logic into create_trial
        return {
            "seq": arg.seq,
            "name": name,
            "request_time": req_time.isoformat(),
            "status": 'failure',
            "path": arg.req.path,
            "queries": arg.req.qs,
            "headers": arg.req.headers,
            "one": {
                "url": url_one
            },
            "other": {
                "url": url_other
            }
        }

    res_one: Response = res2res(Response.from_requests(r_one, arg.default_response_encoding_one), arg.req)
    res_other: Response = res2res(Response.from_requests(r_other, arg.default_response_encoding_other), arg.req)

    dict_one: TOption[dict] = res2dict(res_one)
    dict_other: TOption[dict] = res2dict(res_other)

    # Create diff
    # Either dict_one or dic_other is None, it means that it can't be analyzed, therefore return None
    ddiff = None if dict_one.is_none() or dict_other.is_none() \
        else {} if res_one.body == res_other.body \
        else DeepDiff(dict_one.get(), dict_other.get())

    diff_keys: Optional[DiffKeys] = DiffKeys.from_dict({
        "changed": TList(ddiff.get('type_changes', {}).keys() | ddiff.get('values_changed', {}).keys())
            .map(lambda x: x.replace('[', '<').replace(']', '>'))
            .order_by(_),
        "added": TList(ddiff.get('dictionary_item_added', {}) | ddiff.get('iterable_item_added', {}).keys())
            .map(lambda x: x.replace('[', '<').replace(']', '>'))
            .order_by(_),
        "removed": TList(ddiff.get('dictionary_item_removed', {}) | ddiff.get('iterable_item_removed', {}).keys())
            .map(lambda x: x.replace('[', '<').replace(']', '>'))
            .order_by(_)
    }) if ddiff is not None else None

    # Judgement
    status: Status = judgement(res_one, res_other, dict_one, dict_other,
                               name, arg.req.path, arg.req.qs, arg.req.headers, diff_keys)
    status_symbol = "O" if status == Status.SAME else "X"
    log_msg = f"{log_prefix} {status_symbol} ({res_one.status_code} - {res_other.status_code}) <{to_sec(res_one.elapsed):.2f}s - {to_sec(res_other.elapsed):.2f}s> {arg.req.name.get_or(arg.req.path)}" # noqa
    (logger.info_lv2 if status == Status.SAME else logger.info_lv1)(log_msg)

    file_one = file_other = None
    if store_criterion(status, arg.req.path, arg.req.qs, arg.req.headers, res_one, res_other):
        dir = f'{arg.res_dir}/{arg.key}'
        file_one = f'one/({arg.seq}){name}'
        file_other = f'other/({arg.seq}){name}'
        write_to_file(file_one, dir, dump(res_one))
        write_to_file(file_other, dir, dump(res_other))

    return global_addon_executor.apply_did_challenge(DidChallengeAddOnPayload.from_dict({
        "trial": Trial.from_dict({
            "seq": arg.seq,
            "name": name,
            "request_time": req_time.isoformat(),
            "status": status,
            "path": arg.req.path or "No path",
            "queries": arg.req.qs,
            "headers": arg.req.headers,
            "diff_keys": diff_keys,
            "one": {
                "url": res_one.url,
                "status_code": res_one.status_code,
                "byte": len(res_one.body),
                "response_sec": to_sec(res_one.elapsed),
                "content_type": res_one.content_type,
                "mime_type": res_one.mime_type,
                "encoding": res_one.encoding,
                "file": file_one
            },
            "other": {
                "url": res_other.url,
                "status_code": res_other.status_code,
                "byte": len(res_other.body),
                "response_sec": to_sec(res_other.elapsed),
                "content_type": res_other.content_type,
                "mime_type": res_other.mime_type,
                "encoding": res_other.encoding,
                "file": file_other
            }
        })
    })).trial.to_dict()


def create_concurrent_executor(config: Config) -> Tuple[Any, Concurrency]:
    processes = config.processes.get()
    if processes:
        return (
            futures.ProcessPoolExecutor(max_workers=processes),
            Concurrency.from_dict({
                "processes": processes,
                "threads": 1
            })
        )

    threads = config.threads
    return (
        futures.ThreadPoolExecutor(max_workers=threads),
        Concurrency.from_dict({
            "processes": 1,
            "threads": threads
        })
    )


def exec(config: Config, reqs: TList[Request], key: str, retry_hash: Optional[str]) -> Report:
    # Provision
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=config.max_retries))
    s.mount('https://', HTTPAdapter(max_retries=config.max_retries))

    make_dir(f'{config.output.response_dir}/{key}/one')
    make_dir(f'{config.output.response_dir}/{key}/other')

    # Parse inputs to args of multi-thread executor.
    ex_args = TList(reqs).emap(lambda x, i: {
        "seq": i + 1,
        "number_of_request": len(reqs),
        "key": key,
        "session": s,
        "req": x,
        "host_one": config.one.host,
        "host_other": config.other.host,
        "proxy_one": Proxy.from_host(config.one.proxy),
        "proxy_other": Proxy.from_host(config.other.proxy),
        "default_response_encoding_one": config.one.default_response_encoding,
        "default_response_encoding_other": config.other.default_response_encoding,
        "res_dir": config.output.response_dir,
    })

    # Challenge
    title = config.title.get_or("No title")
    description = config.description.get()
    tags = config.tags.get_or([])
    executor, concurrency = create_concurrent_executor(config)

    logger.info_lv1(f"""
--------------------------------------------------------------------------------
| {title}
| ({key})
--------------------------------------------------------------------------------
| {description}
--------------------------------------------------------------------------------
| - {concurrency.processes} processes
| - {concurrency.threads} threads
--------------------------------------------------------------------------------
    """)

    start_time = now()
    with executor as ex:
        trials = TList([r for r in ex.map(challenge, ChallengeArg.from_dicts(ex_args))]).map(
            lambda x: Trial.from_dict(x))
    end_time = now()

    summary = Summary.from_dict({
        "one": {
            "name": config.one.name,
            "host": config.one.host,
            "proxy": config.one.proxy,
            "default_response_encoding": config.one.default_response_encoding,
        },
        "other": {
            "name": config.other.name,
            "host": config.other.host,
            "proxy": config.other.proxy,
            "default_response_encoding": config.other.default_response_encoding,
        },
        "status": trials.group_by(_.status.value).map_values(len).to_dict(),
        "tags": tags,
        "time": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "elapsed_sec": (end_time - start_time).seconds
        },
        "output": config.output.to_dict(),
        "concurrency": concurrency,
    })

    return Report.from_dict({
        "version": __version__,
        "key": key,
        "title": title,
        "description": description,
        "summary": summary.to_dict(),
        "trials": trials.to_dicts(),
        "addons": config.addons.to_dict(),
        "retry_hash": retry_hash,
        "ignores": config.addons.judgement
            .filter(lambda x: x.name.endswith('ignore_properties'))
            .flat_map(lambda x: x.config.map(_["ignores"]).get_or([]))
    })


def hash_from_args(args: Args) -> str:
    return hashlib.sha256((str(now()) + args.to_json()).encode()).hexdigest()


def merge_args2config(args: Args, config: Config) -> Config:
    return Config.from_dict({
        "one": config.one,
        "other": config.other,
        "output": config.output,
        "threads": args.threads.get_or(config.threads),
        "processes": args.processes if args.processes.get() else config.processes,
        "max_retries": args.max_retries.get() if args.max_retries.get() is not None else config.max_retries,
        "title": args.title if args.title.get() else config.title,
        "description": args.description if args.description.get() else config.description,
        "tags": args.tag if args.tag.get() else config.tags,
        "input_files": args.files if args.files.get() else config.input_files,
        "notifiers": config.notifiers,
        "addons": config.addons
    })


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        logger.info_lv1(self.headers)
        http.server.SimpleHTTPRequestHandler.do_GET(self)


def handle_server(port: Optional[int]):
    Handler = ServerHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        logger.info_lv1(f'Serving HTTP on 0.0.0.0 port {port} (http://0.0.0.0:{port}/)')
        httpd.serve_forever()


def handle_init(name: TOption[str]):
    # XXX: Beta: jumeaux init addon
    # TODO: refactoring
    if name.get() == 'addon':
        addon_dir = f'{os.path.abspath(os.path.dirname(__file__))}/sample/addon'
        for f in os.listdir(addon_dir):
            if os.path.isdir(f'{addon_dir}/{f}'):
                shutil.copytree(f'{addon_dir}/{f}', f)
            else:
                shutil.copy(f'{addon_dir}/{f}', f)
            logger.info_lv1(f'✨ [Create] {f}')
        return

    sample_dir = f'{os.path.abspath(os.path.dirname(__file__))}/sample/template'
    target_dir = f'{sample_dir}/{name.get()}'

    if os.path.exists(target_dir):
        for f in ['config.yml', 'requests']:
            shutil.copy(f'{target_dir}/{f}', '.')
            logger.info_lv1(f'✨ [Create] {f}')
        shutil.copytree(f'{target_dir}/api', 'api')
        logger.info_lv1(f'✨ [Create] templates with a api directory')
        return

    if not os.path.exists(target_dir):
        exit(f'''
Please specify a valid name.

✨ [Valid names] ✨
{os.linesep.join(os.listdir(sample_dir))}
        '''.strip())


def main():
    # We can use args only in `main()`
    args: Args = Args.from_dict(docopt(__doc__, version=__version__))
    init_logger(args.v)

    global global_addon_executor
    # TODO: refactoring
    if args.server:
        handle_server(args.port.get_or(8000))
        return

    if args.init:
        handle_init(args.name)
        return

    if args.retry:
        report: Report = Report.from_jsonf(args.report.get())
        config: Config = merge_args2config(args, create_config_from_report(report))
        global_addon_executor = AddOnExecutor(config.addons)
        origin_logs: TList[Request] = report.trials.map(lambda x: Request.from_dict({
            'path': x.path,
            'qs': x.queries,
            'headers': x.headers,
            'name': x.name
        }))
        retry_hash: Optional[str] = report.key
    else:
        config: Config = merge_args2config(args, create_config(args.config.get() or TList(['config.yml']),
                                                               args.skip_addon_tag))
        global_addon_executor = AddOnExecutor(config.addons)
        origin_logs: TList[Request] = config.input_files.get().flat_map(
            lambda f: global_addon_executor.apply_log2reqs(
                Log2ReqsAddOnPayload.from_dict({
                    'file': f
                })
            )
        )
        retry_hash: Optional[str] = None

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=config.output.encoding)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=config.output.encoding)

    logger.info_lv1(f"""
        ____  _             _         _
__/\__ / ___|| |_ __ _ _ __| |_      | |_   _ _ __ ___   ___  __ _ _   ___  __ __/\__
\    / \___ \| __/ _` | '__| __|  _  | | | | | '_ ` _ \ / _ \/ _` | | | \ \/ / \    /
/_  _\  ___) | || (_| | |  | |_  | |_| | |_| | | | | | |  __/ (_| | |_| |>  <  /_  _\\
  \/   |____/ \__\__,_|_|   \__|  \___/ \__,_|_| |_| |_|\___|\__,_|\__,_/_/\_\   \/

Version: {__version__}
    """)

    if config.output.logger.get():
        logger.warning('`output.logger` is no longer works.')
        logger.warning('And this will be removed soon! You need to remove this property not to stop!')

    logger.info_lv3(f"""
         ____             __ _
__/\__  / ___|___  _ __  / _(_) __ _  __/\__
\    / | |   / _ \| '_ \| |_| |/ _` | \    /
/_  _\ | |__| (_) | | | |  _| | (_| | /_  _\\
  \/    \____\___/|_| |_|_| |_|\__, |   \/
                               |___/
(Merge with yaml files or report, and args)

----

{config.to_yaml()}

""")

    # Requests
    logs: TList[Request] = global_addon_executor.apply_reqs2reqs(
        Reqs2ReqsAddOnPayload.from_dict({'requests': origin_logs}),
        config
    ).requests

    report: Report = global_addon_executor.apply_final(FinalAddOnPayload.from_dict({
        'report': exec(config, logs, hash_from_args(args), retry_hash),
        'output_summary': config.output
    })).report

    print(report.to_pretty_json())


if __name__ == '__main__':
    main()
