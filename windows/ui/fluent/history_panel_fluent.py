"""
历史面板模块
显示剪贴板历史记录列表
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame
)
from PyQt6.QtGui import QWheelEvent

from models.clipboard_item import ClipboardItem
from ui.fluent.item_widget_fluent import ItemWidget
from utils.theme import get_current_theme, get_history_panel_stylesheet


class HistoryPanel(QWidget):
    """历史记录面板控件"""

    # 信号：项被选中
    item_selected = pyqtSignal(ClipboardItem)
    # 信号：收藏状态改变
    favorite_toggled = pyqtSignal(ClipboardItem)
    # 信号：复制请求
    copy_requested = pyqtSignal()
    # 信号：删除请求
    delete_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.items: list[ClipboardItem] = []
        self.item_widgets: list[ItemWidget] = []
        self.selected_item: ClipboardItem = None
        self.selectedIndex = -1

        self._init_ui()

    def _init_ui(self) -> None:
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # 内容容器
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)
        self.content_layout.addStretch()

        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        self._setup_style()
        self._setup_content_style()

    def _setup_style(self) -> None:
        """设置样式"""
        self.setStyleSheet(get_history_panel_stylesheet())

    def _setup_content_style(self) -> None:
        """设置内容容器样式"""
        from utils.theme import get_current_theme
        theme = get_current_theme()
        self.content_widget.setStyleSheet(f"""
            QWidget#content_widget {{
                background-color: {theme['background']};
            }}
        """)

    def set_items(self, items: list[ClipboardItem]) -> None:
        """设置历史项列表"""
        self.items = items
        self._refresh_items()
        self.selectedIndex = -1
        self.selected_item = None

    def _refresh_items(self) -> None:
        """刷新项显示"""
        # 清除现有控件
        for widget in self.item_widgets:
            widget.deleteLater()

        self.item_widgets.clear()

        # 创建新控件
        for item in self.items:
            widget = ItemWidget(item)
            widget.clicked.connect(lambda i=item: self._on_item_clicked(i))
            widget.favorite_toggled.connect(lambda i=item: self._on_favorite_toggled(i))

            # 插入到stretch之前
            self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
            self.item_widgets.append(widget)

    def _on_item_clicked(self, item: ClipboardItem) -> None:
        """项点击处理"""
        # 更新选中状态
        for i, widget in enumerate(self.item_widgets):
            if widget.item == item:
                widget.set_selected(True)
                self.selectedIndex = i
                self.selected_item = item
            else:
                widget.set_selected(False)

        self.item_selected.emit(item)

    def _on_favorite_toggled(self, item: ClipboardItem) -> None:
        """收藏状态切换"""
        self.favorite_toggled.emit(item)

    def select_next(self) -> None:
        """选择下一项"""
        if not self.item_widgets:
            return

        if self.selectedIndex < len(self.item_widgets) - 1:
            self.selectedIndex += 1
        else:
            self.selectedIndex = 0

        self._update_selection()

    def select_previous(self) -> None:
        """选择上一项"""
        if not self.item_widgets:
            return

        if self.selectedIndex > 0:
            self.selectedIndex -= 1
        else:
            self.selectedIndex = len(self.item_widgets) - 1

        self._update_selection()

    def _update_selection(self) -> None:
        """更新选中状态"""
        for i, widget in enumerate(self.item_widgets):
            widget.set_selected(i == self.selectedIndex)

        if 0 <= self.selectedIndex < len(self.item_widgets):
            self.selected_item = self.item_widgets[self.selectedIndex].item
            self.item_selected.emit(self.selected_item)
            self._scroll_to_selected()

    def _scroll_to_selected(self) -> None:
        """滚动到选中项"""
        if 0 <= self.selectedIndex < len(self.item_widgets):
            widget = self.item_widgets[self.selectedIndex]
            self.scroll_area.ensureWidgetVisible(widget)

    def get_selected_item(self) -> ClipboardItem:
        """获取选中项"""
        if 0 <= self.selectedIndex < len(self.item_widgets):
            return self.item_widgets[self.selectedIndex].item
        return None

    def wheelEvent(self, event: QWheelEvent) -> None:
        """鼠标滚轮事件"""
        # 获取滚轮滚动的角度
        delta = event.angleDelta().y()

        # 获取当前滚动条位置
        scroll_bar = self.scroll_area.verticalScrollBar()

        # 每次滚动的像素量
        scroll_step = 50

        # 设置新的滚动位置
        if delta > 0:
            scroll_bar.setValue(scroll_bar.value() - scroll_step)
        else:
            scroll_bar.setValue(scroll_bar.value() + scroll_step)

        event.accept()