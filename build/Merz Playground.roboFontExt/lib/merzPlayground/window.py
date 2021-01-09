import AppKit
import Quartz
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
import merz
from mojo.UI import CodeEditor
from lib.scripting.codeEditor import OutPutEditor
from lib.scripting.scriptTools import ScriptRunner
from lib.tools.defaults import getDefault, setDefault


class MerzPlaygroundWindowController(BaseWindowController):

    windowAutoSaveName = "MerzPlaygroundWindow"

    def __init__(self):
        self.w = vanilla.Window((400, 400), "Merz Playground", minSize=(200, 200))
        self.w.getNSWindow().setFrameUsingName_(self.windowAutoSaveName)

        # Code
        # ----
        self.codeGroup = vanilla.Group((0, 0, 0, 0))
        self.codeEditor = self.codeGroup.codeEditor = CodeEditor((0, 0, -0, -45))
        self.runButton = self.codeGroup.runButton = vanilla.Button(
            (15, -35, -15, 20),
            "Run",
            callback=self.runCode
        )
        self.runButton.bind("r", ["command"])
        self.outputEditor = OutPutEditor((0, 0, -0, -0), readOnly=True)

        paneDescriptions = [
            dict(
                view=self.codeGroup,
                identifier="codeGroup",
                minSize=50,
                canCollapse=False
            ),
            dict(
                view=self.outputEditor,
                identifier="outputEditor",
                size=100,
                minSize=50,
                canCollapse=False
            ),
        ]
        self.codeSplitView = vanilla.SplitView(
            (0, 0, 0, 0),
            paneDescriptions,
            isVertical=False
        )

        # Merz
        # ----
        self.merzView = merz.MerzView((0, 0, 0, 0), backgroundColor=(1, 1, 1, 1))

        # Splits
        # ------
        paneDescriptions = [
            dict(
                view=self.codeSplitView,
                identifier="codeSplitView",
                minSize=50,
                canCollapse=False
            ),
            dict(
                view=self.merzView,
                identifier="merzView",
                minSize=50
            )
        ]
        self.w.splitView = vanilla.SplitView(
            (0, 0, 0, 0),
            paneDescriptions
        )

        self.setUpBaseWindowBehavior()
        self.w.open()


    def runCode(self, sender=None):
        code = self.codeEditor.get()
        container = self.merzView.getMerzContainer()
        container.clearSublayers()
        namespace = dict(
            container=container,
            merz=merz
        )
        if getDefault("PyDEClearOutput", True):
            self.outputEditor.clear()
        self.output = []
        self.stdout = StdOutput(self.output)
        self.stderr = StdOutput(self.output, True)
        ScriptRunner(
            code,
            "<Merz Playground>",
            namespace=namespace,
            stdout=self.stdout,
            stderr=self.stderr
        )
        for text, isError in self.output:
            self.outputEditor.append(text, isError)
        self.output = None
        self.stdout = None
        self.stderr = None


# -----
# Tools
# -----

class StdOutput(object):

    def __init__(self, output, isError=False):
        self.data = output
        self.isError = isError

    def write(self, data):
        self.data.append((data, self.isError))

    def flush(self):
        pass

    def close(self):
        pass


if __name__ == "__main__":
    MerzPlaygroundWindowController()