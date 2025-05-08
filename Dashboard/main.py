# Aqui vai ser a main, onde vamos inicializar o Dashboard

import tkinter as tk
from View import InterfaceDashboard
from control import ControleDashboard

if __name__ == "__main__":
    Dashboard = tk.Tk()
    Interface = InterfaceDashboard(Dashboard)
    Controle = ControleDashboard(Interface)
    Dashboard.mainloop()
