import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle

class ElectricFieldApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.charges = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Simulatore Campo Elettrico')
        self.setGeometry(100, 100, 1280, 720)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Plot canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Buttons
        btn_layout = QVBoxLayout()
        
        self.btn_add_positive = QPushButton('Add positive charge (+)')
        self.btn_add_positive.clicked.connect(lambda: self.set_charge_mode(1))
        btn_layout.addWidget(self.btn_add_positive)
        
        self.btn_add_negative = QPushButton('Add negative charge (-)')
        self.btn_add_negative.clicked.connect(lambda: self.set_charge_mode(-1))
        btn_layout.addWidget(self.btn_add_negative)
        
        self.btn_clear = QPushButton('Delete All')
        self.btn_clear.clicked.connect(self.clear_charges)
        btn_layout.addWidget(self.btn_clear)
        
        self.status_label = QLabel('Ready - Click to add a charge')
        btn_layout.addWidget(self.status_label)
        
        layout.addLayout(btn_layout)
        
        # State variables
        self.charge_mode = 0  # 0 = neutral, 1 = positive, -1 = negative
        
        # Click on graph event handler
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Draw init graph
        self.update_plot()
        
    def set_charge_mode(self, mode):
        self.charge_mode = mode
        sign = '+' if mode == 1 else '-'
        self.status_label.setText(f'Mode: add charge {sign} - Click on the graph')
        
    def on_click(self, event):
        if event.inaxes is not None and self.charge_mode != 0:
            x, y = event.xdata, event.ydata
            self.charges.append((x, y, 1e-9 * self.charge_mode))
            self.update_plot()
        
    def clear_charges(self):
        self.charges = []
        self.charge_mode = 0
        self.status_label.setText('Ready - Click to add a charge')
        self.update_plot()
        
    def calculate_field(self, x, y):
        Ex, Ey = 0, 0
        k = 9e9  # Electrostatic costant
        
        for xc, yc, q in self.charges:
            dx = x - xc
            dy = y - yc
            r = np.sqrt(dx**2 + dy**2)
            
            if r > 0.05:
                E = k * q / r**3
                Ex += E * dx
                Ey += E * dy
                
        return Ex, Ey
        
    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Draw charges
        for x, y, q in self.charges:
            color = 'red' if q > 0 else 'blue'
            ax.add_patch(Circle((x, y), 0.1, color=color))
            ax.text(x, y, '+' if q > 0 else '-', ha='center', va='center', color='white')
        
        # Draw force lines
        if self.charges:
            n_lines = 12
            density = 20
            
            for x, y, q in self.charges:
                angles = np.linspace(0, 2*np.pi, n_lines, endpoint=False)
                
                for angle in angles:
                    dx, dy = np.cos(angle), np.sin(angle)
                    if q < 0:
                        dx, dy = -dx, -dy
                    
                    x_line = [x + 0.15*dx]
                    y_line = [y + 0.15*dy]
                    
                    for _ in range(density*100):
                        Ex, Ey = self.calculate_field(x_line[-1], y_line[-1])
                        E_mag = np.sqrt(Ex**2 + Ey**2)
                        
                        if E_mag < 0.1:
                            break
                        
                        dx = Ex / E_mag * 0.2
                        dy = Ey / E_mag * 0.2
                        
                        x_line.append(x_line[-1] + dx)
                        y_line.append(y_line[-1] + dy)
                        
                        if (x_line[-1] < -2 or x_line[-1] > 2 or 
                            y_line[-1] < -2 or y_line[-1] > 2):
                            break
                            
                    ax.plot(x_line, y_line, color='black', lw=1)
        
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.set_title('Electric field\' force lines')
        ax.grid(True)
        
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ElectricFieldApp()
    ex.show()
    sys.exit(app.exec_())