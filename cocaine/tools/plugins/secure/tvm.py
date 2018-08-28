import logging

from tornado import gen

from cocaine.decorators import coroutine

from . import SecurePlugin


log = logging.getLogger(__name__)


class TVM(SecurePlugin):
    def __init__(self, repo, client_id, client_secret):
        super(TVM, self).__init__(repo)
        self._client_id = client_id
        self._client_secret = client_secret

        self._tvm = repo.create_service('tvm2')

    def ty(self):
        return 'TVM2'

    @coroutine
    def fetch_token(self):
        channel = yield self._tvm.ticket(self._client_id, self._client_secret)
        ticket = yield channel.rx.get()
        log.debug('exchanged client secret with TVM ticket')
        raise gen.Return(self._make_header(ticket))

    def _make_header(self, ticket):
        return '{} {}'.format(self.ty(), ticket)
