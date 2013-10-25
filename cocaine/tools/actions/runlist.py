from cocaine.futures import chain
from cocaine.tools import actions
from cocaine.tools.actions import CocaineConfigReader
from cocaine.tools.printer import printer
from cocaine.tools.tags import RUNLISTS_TAGS

__author__ = 'Evgeny Safronov <division494@gmail.com>'


class Specific(actions.Specific):
    def __init__(self, storage, name):
        super(Specific, self).__init__(storage, 'runlist', name)


class List(actions.List):
    def __init__(self, storage):
        super(List, self).__init__('runlists', RUNLISTS_TAGS, storage)


class View(actions.View):
    def __init__(self, storage, name):
        super(View, self).__init__(storage, 'runlist', name, 'runlists')


class Upload(Specific):
    def __init__(self, storage, name, runlist):
        super(Upload, self).__init__(storage, name)
        self.runlist = runlist
        if not self.runlist:
            raise ValueError('Please specify runlist file path')

    @chain.source
    def execute(self):
        runlist = CocaineConfigReader.load(self.runlist)
        with printer('Uploading runlist "%s"', self.name):
            yield self.storage.write('runlists', self.name, runlist, RUNLISTS_TAGS)


class Create(Specific):
    def execute(self):
        return Upload(self.storage, self.name, '{}').execute()


class Remove(Specific):
    @chain.source
    def execute(self):
        with printer('Removing runlist "%s"', self.name):
            yield self.storage.remove('runlists', self.name)


class AddApplication(Specific):
    def __init__(self, storage, name, app, profile, force=False):
        super(AddApplication, self).__init__(storage, name)
        self.app = app
        self.profile = profile
        self.force = force
        if not self.app:
            raise ValueError('Please specify application name')
        if not self.profile:
            raise ValueError('Please specify profile')

    @chain.source
    def execute(self):
        with printer('Checking runlists') as notify:
            runlists = yield List(self.storage).execute()
            status = 'found' if self.name in runlists else 'not found'
            notify(status)

        if self.name not in runlists:
            if self.force:
                with printer('Runlist does not exist.'):
                    yield Create(self.storage, self.name).execute()

        with printer('Editing runlist "%s"', self.name):
            runlist = yield View(self.storage, name=self.name).execute()
            runlist[self.app] = self.profile

        yield Upload(self.storage, name=self.name, runlist=runlist).execute()
