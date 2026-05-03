from __future__ import annotations
from dsviper import *
from ge import *
import ge.attachments as gea


state = ctx.state()
for a in state.definitions().attachments():
    for k in state.attachment_getting().keys(a):
        trace = state.commit_state_tracing().trace(a,k)
        print("\n-----", k.description(), "-----")
        for p in trace.programs():
            for o in p.trace().opcodes():
                commit_id = str(p.header().commit_id())[:8] + "..."
                print(commit_id, p.trace().enabled(), o.opcode().type(), o.opcode().arguments(state.definitions()))


#for op in state.traced_opcodes():
#    print(op.type(), op.arguments(state.definitions()))

