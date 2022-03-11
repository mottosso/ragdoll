
import os
import json
from maya import cmds
from PySide2 import QtCore, QtWidgets, QtGui
from ._base import FramelessDialog
from ..vendor.qargparse import px
from ..vendor import cmdx
from ..dump import Registry


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


with open(_resource("ui", "style.css")) as f:
    stylesheet = f.read()


def _scaled_stylesheet(style):
    """Replace any mention of <num>px with scaled version

    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.

    """

    output = []
    for line in style.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            key, value = line.rsplit(" ", 1)
            value = px(int(value[:-3]))
            line = "%s %dpx;" % (key, value)
        output += [line]
    result = "\n".join(output)
    result = result % {"res": _resource().replace("\\", "/")}
    return result


def elide(dag_path, length):
    dag_path = str(dag_path)
    placeholder = "..."
    length -= len(placeholder)

    if len(dag_path) <= length:
        return dag_path

    if "|" in dag_path:
        included = []
        parents, base = dag_path.rsplit("|", 1)
        for part in parents.split("|"):
            included.append(part)
            if sum(map(len, included + [base])) > length:
                break

        dag_path = "|".join(included + [base])

    half = int(length / 2)
    return dag_path[:half] + placeholder + dag_path[-half:]


def compute_solver_size(registry, solver):
    # note: maybe we could lru_cache this
    solver_size = 0
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        if scene_comp["entity"] == solver["ragdollId"]:
            solver_size += 1
    return solver_size


def get_all_solver_size(registry):
    solvers = list(registry.view("SolverComponent"))
    solver_size = dict.fromkeys(solvers, 0)
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        solver_size[scene_comp["entity"]] += 1
    return solver_size


def solver_ui_name_by_sizes(solver_sizes, solver):
    solver_id = int(solver["ragdollId"])
    solver_size = solver_sizes[solver_id]

    has_same_size = any(
        _id != solver_id and size == solver_size
        for _id, size in solver_sizes.items()
    )
    transform = solver.parent()
    ui_name = transform.shortest_path() if has_same_size else transform.name()

    _count = len(solver_sizes)
    length = 23 if _count == 3 else 46 if _count == 2 else 69

    return elide(ui_name, length)


class TippedLabel(QtWidgets.QLabel):
    tip_shown = QtCore.Signal(str)

    def enterEvent(self, event):
        # type: (QtCore.QEvent) -> None
        self.tip_shown.emit(self.toolTip() or "")

    def leaveEvent(self, event):
        # type: (QtCore.QEvent) -> None
        self.tip_shown.emit("")


class SolverButton(QtWidgets.QPushButton):
    tip_shown = QtCore.Signal(str)

    def __init__(self, solver_sizes, solver=None, parent=None):
        # type: (dict, cmdx.DagNode, QtWidgets.QWidget) -> None
        super(SolverButton, self).__init__(parent=parent)

        body = QtWidgets.QWidget()
        info = QtWidgets.QWidget()

        _icon_img = _resource("icons", "solver.png")
        _pixmap = QtGui.QIcon(_icon_img).pixmap(px(24))
        _pixmap = _pixmap.scaledToWidth(px(24), QtCore.Qt.SmoothTransformation)
        icon = QtWidgets.QLabel()
        icon.setPixmap(_pixmap)

        val_name = TippedLabel()
        val_size = TippedLabel()

        layout = QtWidgets.QGridLayout(info)
        layout.addWidget(val_name, 0, 1, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(val_size, 1, 1, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(icon)
        layout.addWidget(info, stretch=True, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body, alignment=QtCore.Qt.AlignLeft)

        val_name.tip_shown.connect(self.tip_shown)
        val_size.tip_shown.connect(self.tip_shown)

        self._solver_sizes = solver_sizes
        self._name = val_name
        self._size = val_size
        self._dag_path = None

        if solver is not None:
            self.set_solver(solver)

    def sizeHint(self):
        # type: () -> QtCore.QSize
        size = QtCore.QSize()
        for child in self.children():
            if isinstance(child, QtWidgets.QLayout):
                size += child.sizeHint()
        # expand a bit
        size += QtCore.QSize(4, 4)
        return size

    @property
    def dag_path(self):
        return self._dag_path

    def set_solver(self, solver):
        solver_name = solver_ui_name_by_sizes(self._solver_sizes, solver)
        solver_size = self._solver_sizes[int(solver["ragdollId"])]

        self._name.setText(solver_name)
        self._size.setText(str(solver_size))

        self._name.setToolTip("Shortest name of this solver:\n %s"
                              % solver.dag_path())
        self._size.setToolTip("Size of the solver. The sum of all component "
                              "related to this solver, e.g. count of markers, "
                              "constraints, and other ragdoll nodes.")

        self._dag_path = solver.shortest_path()


class SolverComboBox(QtWidgets.QComboBox):

    def __init__(self, solver_sizes, solvers=None, parent=None):
        # type: (dict, list[cmdx.DagNode], QtWidgets.QWidget) -> None
        super(SolverComboBox, self).__init__(parent=parent)

        _icon = QtGui.QIcon(_resource("icons", "solver.png"))
        for i, solver in enumerate(solvers):
            solver_name = solver_ui_name_by_sizes(solver_sizes, solver)
            solver_size = solver_sizes[int(solver["ragdollId"])]

            item_name = "[%d] %s" % (solver_size, solver_name)
            self.addItem(_icon, item_name, solver)


class SolverSelectorDialog(FramelessDialog):
    solver_picked = QtCore.Signal(str)

    def __init__(self, solvers, best_guess=None, parent=None):
        """
        Args:
            solvers (list[cmdx.DagNode]):
            best_guess (cmdx.DagNode or None):
            parent (QtWidgets.QWidget or None):
        """
        super(SolverSelectorDialog, self).__init__(parent=parent)

        dump = json.loads(cmds.ragdollDump())
        registry = Registry(dump)
        solver_sizes = get_all_solver_size(registry)
        # todo: check ragdollDump schema version ?

        body = QtWidgets.QWidget()
        title = QtWidgets.QLabel("Pick Solver")
        title.setStyleSheet("QLabel {font-size: 24px;}")

        if len(solvers) > 3:
            view = self._init_full(solver_sizes, solvers, best_guess)
        else:
            view = self._init_slim(solver_sizes, solvers)

        # note: this dialog has fixed width by the banner
        footer = RoundedFooter()

        hint = QtWidgets.QTextEdit()
        hint.setObjectName("Hint")
        hint.setParent(footer)
        hint.setReadOnly(True)
        hint.setLineWrapMode(hint.WidgetWidth)
        helptext = "Pro tip: To avoid this dialog, select a marker before " \
                   "calling the Manipulator"
        hint.setProperty("defaultText", helptext)
        hint.setText(helptext)
        hint.move(px(30), px(9))
        hint.setFixedWidth(px(400))
        hint.setFixedHeight(px(75))
        hint.setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(18, 24, 18, 8)
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(view)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.setStyleSheet(_scaled_stylesheet(stylesheet))

        self._hint = hint

    def on_tip_shown(self, text):
        self._hint.setText(text or self._hint.property("defaultText"))

    def _init_slim(self, solver_sizes, solvers):
        # type: (dict, list[cmdx.DagNode]) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(solver_sizes, s) for s in solvers]

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)
            btn.tip_shown.connect(self.on_tip_shown)

        self._solvers = solver_btn_row
        self._combo = None

        return view

    def _init_full(self, solver_sizes, solvers, best_guess=None):
        # type: (dict, list[cmdx.DagNode], cmdx.DagNode) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(solver_sizes)]
        solver_combo = SolverComboBox(solver_sizes, solvers)

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)
        layout.addWidget(solver_combo)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)
            btn.tip_shown.connect(self.on_tip_shown)
        solver_combo.currentIndexChanged.connect(self.on_solver_changed)

        self._solvers = solver_btn_row
        self._combo = solver_combo

        # init
        if best_guess is None:
            self.on_solver_changed(0)
        else:
            assert best_guess in solvers
            solver_combo.setCurrentIndex(solvers.index(best_guess))
            if solver_combo.currentIndex() == 0:
                self.on_solver_changed(0)

        return view

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()

    def on_solver_changed(self, index):
        solver = self._combo.itemData(index)
        self._solvers[-1].set_solver(solver)


class RoundedFooter(QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        super(RoundedFooter, self).__init__(*args, **kwargs)
        self.setObjectName("Background")
        self.setFixedHeight(px(75))
        self.setFixedWidth(px(570))

        pixmap = QtGui.QPixmap(_resource("ui", "option_header.png"))
        pixmap = pixmap.scaledToWidth(px(570), QtCore.Qt.SmoothTransformation)

        self._image = pixmap

    def paintEvent(self, event):
        r = px(10)
        w = self.width()
        h = self.height()

        # make a half rounded rect (sharped top, rounded bottom)
        #   ___________________
        #  |                  |
        #  |                  |
        #  \_________________/
        #
        path = QtGui.QPainterPath()
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(QtCore.QRect(0, 0, w, h), r, r)
        path.addRect(QtCore.QRect(0, 0, r, r))
        path.addRect(QtCore.QRect(w - r, 0, r, r))

        painter = QtGui.QPainter(self)
        painter.setClipPath(path.simplified())
        painter.setRenderHint(painter.Antialiasing)
        painter.drawPixmap(0, 0, self._image)
