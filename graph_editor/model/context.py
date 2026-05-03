from __future__ import annotations

from dsviper import CommitStore, CommitDatabase, CommitState, CommitMutableState, ValueCommitId

from ge import attachments, definitions
from ge.data import Graph_GraphKey
from model import graph


class Context:

    @classmethod
    def instance(cls) -> Context:
        if not hasattr(cls, "_instance"):
            setattr(cls, "_instance", cls())
        return getattr(cls, "_instance")

    def __init__(self):
        self.store = CommitStore()
        self.graph_key = Graph_GraphKey.create()

    def create_database(self, file_path: str) -> CommitDatabase:
        result = CommitDatabase.create(file_path, documentation="A Graph Editor Commit Database")
        result.extend_definitions(definitions.definitions())
        return result

    def use(self, database: CommitDatabase):
        if not database.commit_ids():
            self._create_initial_commit(database, database.initial_state())

        commit_id = database.last_commit_id()
        self.store.set_state(database.state(commit_id))
        self.store.set_database(database)
        self.store.notify_database_did_open()

        self.load()

    def close(self):
        self.store.close()

    def load(self):
        if not self.store.has_database():
            raise Exception("CommitStoreErrors::noDatabase")

        commit_id = self.store.database().last_commit_id()
        self.store.use_commit(commit_id)
        self.graph_key = self._load_first_graph()
        self.store.reset_undo_redo()
        self.store.notify_state_did_change()

    def new_graph(self):
        if not self.store.has_database():
            raise Exception("CommitStoreErrors::noDatabase")

        attachment = self.store.state().definitions().check_attachment(
            definitions.AttachmentRuntimeIds.Graph_Graph_Description)
        count = len(self.store.state().attachment_getting().keys(attachment)) + 1
        self.use_new_graph(f"G{count}")

    def use_new_graph(self, label: str):
        commit_id, new_graph_id = self._create_graph(self.store.database(), self.store.state(), label)

        self.graph_key = new_graph_id
        self.store.use_commit(commit_id)
        self.store.reset_undo_redo()
        self.store.notify_state_did_change()

    def reset(self):
        if not self.store.has_database():
            raise Exception("CommitStoreErrors::noDatabase")

        self.store.notify_database_will_reset()
        self.store.database().reset_commits()
        self.store.notify_database_did_reset()

        self.load()

    def _create_initial_commit(self, database: CommitDatabase, state: CommitState) -> tuple[
        ValueCommitId, Graph_GraphKey]:
        return self._create_graph(database, state, "G1")

    def _create_graph(self, database: CommitDatabase, state: CommitState, label: str) -> tuple[
        ValueCommitId, Graph_GraphKey]:
        mutable_state = CommitMutableState(state)
        graph_key = graph.create(mutable_state.attachment_mutating(), label)
        commit_id = database.commit_mutations(f"New Graph '{label}'", mutable_state)

        return commit_id, graph_key

    # --- Facade for Python Editor

    def dispatch(self, label: str, func, *args):
        """Dispatch a mutation — ctx.dispatch("label", func, key, ...)."""
        self.store.dispatch(label, func, *args)

    def undo(self):
        self.store.undo()

    def redo(self):
        self.store.redo()

    # Store state
    def has_database(self): return self.store.has_database()
    def database(self): return self.store.database()
    def state(self): return self.store.state()
    def attachment_getting(self): return self.store.attachment_getting()
    def mutable_state(self): return self.store.mutable_state()
    def definitions(self): return self.store.database().definitions() if self.store.has_database() else None

    # Store mutations
    def commit_mutations(self, label, ms): self.store.commit_mutations(label, ms)
    def extend_definitions(self, defs): return self.store.database().extend_definitions(defs) if self.store.has_database() else None
    def dispatch_set(self, label, att, key, val): self.store.dispatch_set(label, att, key, val)
    def dispatch_update(self, label, att, key, path, val): self.store.dispatch_update(label, att, key, path, val)
    def dispatch_enable_commit(self, cid, enabled): self.store.dispatch_enable_commit(cid, enabled)

    # Commit operations
    def can_undo(self): return self.store.can_undo()
    def can_redo(self): return self.store.can_redo()
    def forward(self): self.store.forward()
    def reduce_heads(self): self.store.reduce_heads()
    def disable_commit(self, cid): self.store.dispatch_enable_commit(cid, False)
    def enable_commit(self, cid): self.store.dispatch_enable_commit(cid, True)
    def merge_commit(self, cid): self.store.reduce_heads()  # simplified

    def _load_first_graph(self) -> Graph_GraphKey:
        graph_keys = attachments.graph_graph_description_keys(self.store.state().attachment_getting())
        if not graph_keys:
            raise Exception("ContextErrors::missingGraphKey()")

        return graph_keys.min()
