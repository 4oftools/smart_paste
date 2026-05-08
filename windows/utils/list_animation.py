"""
列表项加载动画模块 - Fluent 风格
提供平滑的列表项加载和过渡动画
"""

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup,
    QParallelAnimationGroup, QTimer, QObject, pyqtSignal
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QVBoxLayout
from PyQt6.QtGui import QColor


def _loading_theme():
    """延迟导入避免循环依赖"""
    from utils.theme import get_current_theme
    return get_current_theme()


class ListItemAnimator(QObject):
    """列表项动画器 - Fluent 风格"""

    animation_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animations = []
        self._stagger_delay = 30  # 交错延迟（毫秒）
        self._animation_duration = 200  # 动画时长（毫秒）

    def animate_items_appear(self, widgets: list, start_index: int = 0) -> None:
        """
        动画显示列表项（淡入 + 滑动）
        
        Args:
            widgets: 要动画显示的控件列表
            start_index: 起始索引
        """
        self._animations.clear()

        for i, widget in enumerate(widgets):
            # 设置初始状态
            widget.setGraphicsEffect(QGraphicsOpacityEffect(widget))
            effect = widget.graphicsEffect()
            effect.setOpacity(0)

            # 创建动画
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(self._animation_duration)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            # 交错延迟
            delay = start_index + i * self._stagger_delay
            animation.start(delay)

            self._animations.append(animation)

        # 最后一个动画完成后发送信号
        if widgets:
            last_animation = self._animations[-1]
            last_animation.finished.connect(self.animation_finished.emit)

    def animate_items_disappear(self, widgets: list, 
                                 on_finished=None) -> None:
        """
        动画隐藏列表项（淡出）
        
        Args:
            widgets: 要动画隐藏的控件列表
            on_finished: 完成回调
        """
        self._animations.clear()

        for i, widget in enumerate(widgets):
            effect = widget.graphicsEffect()
            if not effect:
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)

            # 创建动画
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(self._animation_duration)
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)

            # 交错延迟
            delay = i * self._stagger_delay
            animation.start(delay)

            self._animations.append(animation)

        # 最后一个动画完成后回调
        if widgets and on_finished:
            last_animation = self._animations[-1]
            last_animation.finished.connect(on_finished)

    def animate_item_add(self, widget: QWidget, index: int = 0) -> None:
        """
        动画添加单个列表项
        
        Args:
            widget: 要添加的控件
            index: 索引（用于计算延迟）
        """
        # 设置初始状态
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0)
        widget.setGraphicsEffect(effect)

        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(self._animation_duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 延迟启动
        QTimer.singleShot(index * self._stagger_delay, animation.start)

    def animate_item_remove(self, widget: QWidget, 
                            on_finished=None) -> None:
        """
        动画移除单个列表项
        
        Args:
            widget: 要移除的控件
            on_finished: 完成回调
        """
        effect = widget.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(self._animation_duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()

    def set_stagger_delay(self, delay: int) -> None:
        """
        设置交错延迟
        
        Args:
            delay: 延迟毫秒数
        """
        self._stagger_delay = delay

    def set_animation_duration(self, duration: int) -> None:
        """
        设置动画时长
        
        Args:
            duration: 时长毫秒数
        """
        self._animation_duration = duration

    def stop_all_animations(self) -> None:
        """停止所有动画"""
        for animation in self._animations:
            animation.stop()
        self._animations.clear()


class LoadingIndicator(QWidget):
    """加载指示器 - Fluent 风格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_animation()
        self.hide()

    def _setup_ui(self) -> None:
        """设置 UI"""
        self.setFixedSize(200, 100)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 加载标签
        self.loading_label = LoadingLabel()
        layout.addWidget(self.loading_label)

        self.setLayout(layout)

        # 样式（随当前主题）
        theme = _loading_theme()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['overlay']};
                border-radius: 12px;
            }}
        """)
        self.loading_label.setStyleSheet(f"""
            QLabel, QWidget {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
        """)

    def _setup_animation(self) -> None:
        """设置动画"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def start_loading(self) -> None:
        """开始加载"""
        self.show()
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        self.loading_label.start_animation()

    def stop_loading(self) -> None:
        """停止加载"""
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        self.loading_label.stop_animation()


class LoadingLabel(QWidget):
    """加载动画标签"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dot_count = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_dots)
        self.setText("加载中")

    def _setup_ui(self) -> None:
        """设置 UI（使用当前主题文字色）"""
        theme = _loading_theme()
        self.setStyleSheet(f"""
            QLabel, QWidget {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
        """)

    def setText(self, text: str) -> None:
        """设置文本"""
        self._base_text = text
        self._update_dots()

    def _update_dots(self) -> None:
        """更新点动画"""
        self._dot_count = (self._dot_count + 1) % 4
        dots = "." * self._dot_count
        super().setText(f"{self._base_text}{dots}")

    def start_animation(self) -> None:
        """开始动画"""
        self._timer.start(500)

    def stop_animation(self) -> None:
        """停止动画"""
        self._timer.stop()
        self._dot_count = 0
        super().setText(self._base_text)


class StaggeredAnimation:
    """交错动画工具类"""

    @staticmethod
    def animate_list(items: list, 
                     animation_func,
                     stagger_delay: int = 30,
                     duration: int = 200) -> None:
        """
        为列表项应用交错动画
        
        Args:
            items: 列表项
            animation_func: 动画函数
            stagger_delay: 交错延迟
            duration: 动画时长
        """
        for i, item in enumerate(items):
            QTimer.singleShot(
                i * stagger_delay,
                lambda widget=item: animation_func(widget, duration)
            )

    @staticmethod
    def fade_in_list(widgets: list, 
                     stagger_delay: int = 30,
                     duration: int = 200) -> None:
        """
        列表淡入
        
        Args:
            widgets: 控件列表
            stagger_delay: 交错延迟
            duration: 动画时长
        """
        for i, widget in enumerate(widgets):
            effect = QGraphicsOpacityEffect(widget)
            effect.setOpacity(0)
            widget.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(duration)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            QTimer.singleShot(i * stagger_delay, animation.start)

    @staticmethod
    def slide_in_list(widgets: list,
                      direction: str = 'bottom',
                      stagger_delay: int = 30,
                      duration: int = 200) -> None:
        """
        列表滑入
        
        Args:
            widgets: 控件列表
            direction: 方向
            stagger_delay: 交错延迟
            duration: 动画时长
        """
        for i, widget in enumerate(widgets):
            # 实现滑动逻辑
            StaggeredAnimation.fade_in_list(
                [widget], 
                stagger_delay=i * stagger_delay,
                duration=duration
            )
