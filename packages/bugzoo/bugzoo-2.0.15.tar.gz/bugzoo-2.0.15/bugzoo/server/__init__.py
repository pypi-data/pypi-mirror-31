from typing import Dict, Any
from functools import wraps
import flask

from ..manager import BugZoo
from ..exceptions import *

daemon = None # type: BugZoo
app = flask.Flask(__name__)


def throws_errors(func):
    """
    Wraps a function responsible for implementing an API endpoint such that
    any server errors that are thrown are automatically transformed into
    appropriate HTTP responses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        # if no status code is provided, assume 400
        if isinstance(response, BugZooException):
            err_jsn = flask.jsonify(response.to_dict())
            return err_jsn, 400

        if isinstance(response, tuple) \
           and isinstance(response[0], BugZooException):
            err = response[0] # type: BugZooException
            err_jsn = flask.jsonify(err.to_dict())
            return (err_jsn, response[1:])

        return response

    return wrapper


@app.route('/bugs', methods=['GET'])
def list_bugs():
    jsn = [] # type: List[str]
    for bug in daemon.bugs:
        jsn.append(bug.name)
    return flask.jsonify(jsn)


@app.route('/bugs/<uid>', methods=['GET'])
def show_bug(uid: str):
    jsn = {} # type: Dict[Any, Any]
    try:
        bug = daemon.bugs[uid]
        jsn = bug.to_dict()
    except KeyError:
        # not found
        jsn = {'error': {'code': 'BLAH',
                         'message': 'No bug found with given UID.'}}
    return flask.jsonify(jsn)


# TODO return a job ID
@app.route('/bugs/<uid>/build', methods=['POST'])
@throws_errors
def build_bug(uid: str):
    try:
        bug = daemon.bugs[uid]
    except KeyError:
        return BugNotFound(uid), 404

    # is the bug already installed?
    # TODO add ability to force rebuild
    if daemon.bugs.is_installed(bug):
        return BugAlreadyBuilt(uid), 409

    try:
        daemon.bugs.build(bug)
    except ImageBuildFailed as err:
        return err, 500

    return ('', 204)


@app.route('/bugs/<uid>/provision', methods=['POST'])
@throws_errors
def provision_bug(uid: str):
    try:
        bug = daemon.bugs[uid]
    except KeyError:
        return BugNotFound(uid), 404

    if not daemon.bugs.is_installed(bug):
        return ImageNotInstalled(bug.image), 400

    container = daemon.containers.provision(bug)
    jsn = flask.jsonify(container.to_dict())

    return (jsn, 200)


@app.route('/bugs/<uid>/coverage', methods=['POST'])
@throws_errors
def coverage_bug(uid: str):
    try:
        bug = daemon.bugs[uid]
    except KeyError:
        return BugNotFound(uid), 404

    if not daemon.bugs.is_installed(bug):
        return ImageNotInstalled(bug.image), 400

    try:
        coverage = daemon.bugs.coverage(bug)
    # TODO: work on this
    except:
        return FailedToComputeCoverage("unknown reason"), 500

    jsn = flask.jsonify(coverage.to_dict())
    return (jsn, 200)


@app.route('/containers/<id_container>/test/<id_test>', methods=['POST'])
@throws_errors
def test_container(id_container: str, id_test: str):
    try:
        container = daemon.containers[id_container]
    except KeyError:
        return ContainerNotFound(id_container), 404

    try:
        bug = daemon.bugs[container.bug]
    except KeyError:
        return BugNotFound(container.bug), 500

    try:
        test = bug.harness[id_test]
    except KeyError:
        return TestNotFound(id_test), 404

    outcome = daemon.containers.test(container, test)

    jsn = flask.jsonify(outcome.to_dict())
    return (jsn, 200)


@app.route('/bugs/<uid>/installed', methods=['GET'])
@throws_errors
def is_installed_bug(uid: str):
    try:
        bug = daemon.bugs[uid]
    except KeyError:
        return BugNotFound(uid), 404

    status = daemon.bugs.is_installed(bug)
    return (flask.jsonify(status), 200)


@app.route('/files/<id_container>/<filepath>', methods=['GET'])
@throws_errors
def interact_with_file(id_container: str, filepath: str):
    try:
        container = daemon.containers[id_container]
    except KeyError:
        return ContainerNotFound(id_container), 404

    if flask.request.method == 'GET':
        try:
            return daemon.files.read(container, filepath)
        except KeyError:
            return FileNotFound(filepath), 404


@app.route('/containers', methods=['GET'])
def list_containers():
    jsn = []
    for container in daemon.containers:
        jsn.append(container.uid)
    return flask.jsonify(jsn)


@app.route('/containers/<uid>', methods=['GET'])
@throws_errors
def show_container(uid: str):
    try:
        container = daemon.containers[uid]
    except KeyError:
        return ContainerNotFound(uid), 404

    jsn = flask.jsonify(container.to_dict())
    return (jsn, 200)


@app.route('/containers/<uid>/alive', methods=['GET'])
@throws_errors
def is_alive_container(uid: str):
    try:
        container = daemon.containers[uid]
    except KeyError:
        return ContainerNotFound(uid), 404

    jsn = flask.jsonify(daemon.containers.is_alive(container))
    return (jsn, 200)


@app.route('/containers/<uid>/exec', methods=['POST'])
@throws_errors
def exec_container(uid: str):
    try:
        container = daemon.containers[uid]
    except KeyError:
        return ContainerNotFound(uid), 404

    # TODO: generic bad request error
    args = flask.request.get_json() # type: Dict[str, Any]
    if 'command' not in args:
        return ArgumentNotSpecified("command"), 400

    cmd = args['command']
    context = args.get('context')
    stdout = args.get('stdout', True)
    stderr = args.get('stderr', False)
    time_limit = args.get('time-limit')
    if isinstance(time_limit, int):
        time_limit = float(time_limit)

    assert isinstance(cmd, str)
    assert context is None or isinstance(context, str)
    assert isinstance(stdout, bool)
    assert isinstance(stderr, bool)
    assert time_limit is None or \
        isinstance(time_limit, int) or \
        isinstance(time_limit, float)

    response = daemon.containers.command(container,
                                         cmd=cmd,
                                         context=context,
                                         stdout=stdout,
                                         stderr=stderr,
                                         block=True,
                                         verbose=False,
                                         time_limit=time_limit)

    jsn = flask.jsonify(response.to_dict())
    return (jsn, 200)


# TODO: deal with race condition
@app.route('/containers/<uid>', methods=['DELETE'])
@throws_errors
def delete_container(uid: str):
    try:
        daemon.containers.delete(uid)
        return ('', 204)
    except KeyError:
        return ContainerNotFound(uid), 404


@app.route('/containers', methods=['POST'])
@throws_errors
def provision_container():
    args = flask.request.get_json()

    if 'bug-uid' not in args:
        return ArgumentNotSpecified("bug"), 400
    bug_uid = args['bug-uid']

    try:
        bug = daemon.bugs[bug_uid]
    except KeyError:
        return BugNotFound(bug_uid), 404

    c = daemon.containers.provision(bug)
    return (flask.jsonify(c.uid), 201)


def run(port: int = 6060) -> None:
    global daemon
    daemon = BugZoo()
    app.run(port=port)


def main() -> None:
    run()
