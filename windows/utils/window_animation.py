"""
窗口动画模块 - Fluent 风格
提供平滑的窗口显示/隐藏动画效果
"""

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, 
    QSequentialAnimationGroup, QParallelAnimationGroup,
    QAbstractAnimation
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


class WindowAnimator:
    """窗口动画器 - Fluent 风格"""

    def __init__(self, window: QWidget):
        self.window = window
        self._setup_effects()
        self._setup_animations()

    def _setup_effects(self) -> None:
        """设置图形效果"""
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.window)
        self.window.setGraphicsEffect(self.opacity_effect)

    def _setup_animations(self) -> None:
        """设置动画"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 位置动画（用于滑动效果）
        self.position_animation = QPropertyAnimation(
            self.window, b"pos"
        )
        self.position_animation.setDuration(200)
        self.position_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 组合动画
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.addAnimation(self.position_animation)

    def show_with_animation(self, target_pos: QPoint = None) -> None:
        """
        带动画显示窗口
        
        Args:
            target_pos: 目标位置，如果为 None 则使用当前位置
        """
        if target_pos is None:
            target_pos = self.window.pos()

        # 设置初始状态
        self.opacity_effect.setOpacity(0)
        self.window.setWindowOpacity(0)
        
        # 设置初始位置（向上偏移 20 像素）
        start_pos = target_pos - QPoint(0, 20)
        self.window.move(start_pos)
        
        # 显示窗口
        self.window.show()
        self.window.activateWindow()
        self.window.raise_()

        # 配置动画
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        
        self.position_animation.setStartValue(start_pos)
        self.position_animation.setEndValue(target_pos)

        # 启动动画
        self.animation_group.start()

    def hide_with_animation(self) -> None:
        """带动画隐藏窗口"""
        current_pos = self.window.pos()
        end_pos = current_pos - QPoint(0, 20)  # 向上移动

        # 配置动画
        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setEndValue(0)
        
        self.position_animation.setStartValue(current_pos)
        self.position_animation.setEndValue(end_pos)

        # 动画完成后隐藏窗口
        self.animation_group.finished.connect(self._on_hide_finished)
        self.animation_group.start()

    def _on_hide_finished(self) -> None:
        """隐藏动画完成回调"""
        self.animation_group.finished.disconnect(self._on_hide_finished)
        self.window.hide()

    def fade_in(self, duration: int = 300) -> None:
        """
        淡入效果
        
        Args:
            duration: 动画时长（毫秒）
        """
        animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

    def fade_out(self, duration: int = 300, on_finished=None) -> None:
        """
        淡出效果
        
        Args:
            duration: 动画时长（毫秒）
            on_finished: 完成回调
        """
        animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        if on_finished:
            animation.finished.connect(on_finished)
        
        animation.start()

    def slide_in(self, direction: str = 'bottom', duration: int = 300) -> None:
        """
        滑入效果
        
        Args:
            direction: 方向 ('top', 'bottom', 'left', 'right')
            duration: 动画时长
        """
        current_pos = self.window.pos()
        size = self.window.size()

        # 计算起始位置
        if direction == 'top':
            start_pos = current_pos - QPoint(0, size.height())
        elif direction == 'bottom':
            start_pos = current_pos + QPoint(0, size.height())
        elif direction == 'left':
            start_pos = current_pos - QPoint(size.width(), 0)
        elif direction == 'right':
            start_pos = current_pos + QPoint(size.width(), 0)
        else:
            start_pos = current_pos

        # 位置动画
        pos_animation = QPropertyAnimation(self.window, b"pos")
        pos_animation.setDuration(duration)
        pos_animation.setStartValue(start_pos)
        pos_animation.setEndValue(current_pos)
        pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 透明度动画
        opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(0)
        opacity_animation.setEndValue(1)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 组合动画
        group = QParallelAnimationGroup()
        group.addAnimation(pos_animation)
        group.addAnimation(opacity_animation)

        self.window.show()
        group.start()

    def slide_out(self, direction: str = 'bottom', duration: int = 300, 
                  on_finished=None) -> None:
        """
        滑出效果
        
        Args:
            direction: 方向 ('top', 'bottom', 'left', 'right')
            duration: 动画时长
            on_finished: 完成回调
        """
        current_pos = self.window.pos()
        size = self.window.size()

        # 计算结束位置
        if direction == 'top':
            end_pos = current_pos - QPoint(0, size.height())
        elif direction == 'bottom':
            end_pos = current_pos + QPoint(0, size.height())
        elif direction == 'left':
            end_pos = current_pos - QPoint(size.width(), 0)
        elif direction == 'right':
            end_pos = current_pos + QPoint(size.width(), 0)
        else:
            end_pos = current_pos

        # 位置动画
        pos_animation = QPropertyAnimation(self.window, b"pos")
        pos_animation.setDuration(duration)
        pos_animation.setStartValue(current_pos)
        pos_animation.setEndValue(end_pos)
        pos_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # 透明度动画
        opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(1)
        opacity_animation.setEndValue(0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 组合动画
        group = QParallelAnimationGroup()
        group.addAnimation(pos_animation)
        group.addAnimation(opacity_animation)

        if on_finished:
            group.finished.connect(on_finished)

        group.start()


class FluentEasingCurves:
    """Fluent 风格缓动曲线"""

    @staticmethod
    def default() -> QEasingCurve:
        """默认 Fluent 曲线"""
        return QEasingCurve(QEasingCurve.Type.OutCubic)

    @staticmethod
    def bounce() -> QEasingCurve:
        """弹性效果"""
        return QEasingCurve(QEasingCurve.Type.OutBounce)

    @staticmethod
    def smooth() -> QEasingCurve:
        """平滑效果"""
        curve = QEasingCurve()
        curve.setType(QEasingCurve.Type.Custom)
        # 自定义平滑曲线
        curve.addStop(0.0, 0.0)
        curve.addStop(0.3, 0.3)
        curve.addStop(0.7, 0.8)
        curve.addStop(1.0, 1.0)
        return curve

    @staticmethod
    def quick() -> QEasingCurve:
        """快速效果"""
        return QEasingCurve(QEasingCurve.Type.OutQuad)

    @staticmethod
    def slow() -> QEasingCurve:
        """慢速效果"""
        return QEasingCurve(QEasingCurve.Type.OutQuart)
