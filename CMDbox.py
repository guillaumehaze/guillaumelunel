import sys
import subprocess
import threading
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
    QTextEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout, 
    QGroupBox, QGridLayout, QSystemTrayIcon, QMenu, QAction,
)

from PyQt5.QtCore import Qt, pyqtSignal as Signal, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap, QIcon,QFont

import socket 
import ctypes

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class StreamToSignal:
    """Redirige stdout et stderr vers un signal Qt."""
    def __init__(self, log_signal):
        self.log_signal = log_signal

    def write(self, message):
        if message.strip():
            self.log_signal.emit(message.strip())

    def flush(self):
        pass

    

class LogSignalEmitter(QWidget):
            log_signal = Signal(str)  # Signal pour transmettre les logs
    
            def __init__(self, pc_entry):
                super().__init__()

                self.pc_entry = pc_entry
                self.setWindowTitle("Command Executor")

                # Layout principal
                layout = QVBoxLayout()

                # Ajout de l'interface de commande
                self.command_entry = QLineEdit(self)
                self.command_entry.setPlaceholderText("Entrez la commande à exécuter")
                self.command_entry.setStyleSheet("background-color: #333333; color: white; padding: 5px;")
                layout.addWidget(self.command_entry)

                self.send_button = QPushButton("Envoyer", self)
                self.send_button.clicked.connect(self.on_send_command)
                self.send_button.setStyleSheet("background-color: #3A3A3A; color: white; padding: 10px; font-size: 12px;")
                layout.addWidget(self.send_button)

                self.cancel_button = QPushButton("Annuler", self)
                self.cancel_button.setStyleSheet("background-color: #3A3A3A; color: white; padding: 10px; font-size: px;")
                self.cancel_button.setDisabled(True)
                self.cancel_button.clicked.connect(self.cancel_command)
                layout.addWidget(self.cancel_button)

                # Zone d'affichage des logs
                self.log_console = QTextEdit(self)
                self.log_console.setReadOnly(True)
                self.log_console.setStyleSheet("background-color: #222222; color: #32CD32; font-family: Consolas; padding: 1px;")
                layout.addWidget(self.log_console)

                self.setLayout(layout)

                self.current_process = None

                # Connexion du signal pour afficher les logs
                self.log_signal.connect(self.update_log)

                # Rediriger stdout et stderr vers la zone de logs
                sys.stdout = StreamToSignal(self.log_signal)
                sys.stderr = StreamToSignal(self.log_signal)

            def update_log(self, message):
                """Ajoute un message à la zone de log sans écraser les anciens messages"""
                self.log_console.append(message)

            def on_send_command(self):
                """Fonction appelée lorsque l'utilisateur clique sur 'Envoyer'."""
                pc_name = self.pc_entry.text().strip()
                command = self.command_entry.text().strip()

                if not command:
                    self.log_signal.emit("[ERREUR] Veuillez entrer une commande à exécuter.")
                    return

                self.send_remote_command_thread(pc_name, command)

            def cancel_command(self):
                """Interrompt le processus en cours."""
                if self.current_process:
                    try:
                        self.current_process.terminate()
                        self.log_signal.emit("[INFO] Commande annulée avec succès.")
                    except Exception as e:
                        self.log_signal.emit(f"[ERREUR] Erreur lors de l'annulation : {e}")
                    finally:
                        self.current_process = None
                        self.cancel_button.setDisabled(True)
                else:
                    self.log_signal.emit("[ERREUR] Aucune commande en cours.")

            def send_remote_command_thread(self, pc_name, command):
                """Exécute une commande distante et affiche les résultats en temps réel."""

                def execute_command():
                        if not command:
                            self.log_signal.emit("[ERREUR] Commande invalide.")
                            return

                        psexec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PsExec64.exe")
                        psexec_command = [psexec_path, "-accepteula", "-h", "-s", "-nobanner", f"\\\\{pc_name}", "cmd.exe", "/c", f"{command}"]

                        try:
                            self.current_process = subprocess.Popen(
                                psexec_command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=1,
                                universal_newlines=True
                            )

                            self.cancel_button.setEnabled(True)
                            self.log_signal.emit(f"[INFO] Exécution de '{command}' sur {pc_name}...")

                            # Lire la sortie en temps réel
                            for line in iter(self.current_process.stdout.readline, ''):
                                self.log_signal.emit(line.strip())

                            for error in iter(self.current_process.stderr.readline, ''):
                                self.log_signal.emit(f"{error.strip()}")

                            self.current_process.wait()

                            if self.current_process.returncode == 0:
                                self.log_signal.emit(f"[INFO] Commande exécutée avec succès sur {pc_name}.")
                            else:
                                self.log_signal.emit(f"[ERREUR] Une erreur est survenue (Code {self.current_process.returncode}).")

                        except Exception as e:
                            self.log_signal.emit(f"[ERREUR] Erreur d'exécution : {e}")
                        finally:
                            self.cancel_button.setDisabled(True)
                            self.current_process = None
                            self.log_signal.emit("[INFO] Commande terminée.")


                thread = threading.Thread(target=execute_command, daemon=True)
                thread.start()


class ScanApp(QWidget):
   def __init__(self):
        super().__init__()
        self.initUI()

   def initUI(self):
       
       
        self.setWindowTitle("CMDbox")
        self.setStyleSheet("background-color: #1F1F1F; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(400, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # Barre de titre
        title_bar = QHBoxLayout()
        self.title_label = QLabel("CMDbox 📦", self)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")

        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: #444; color: white; font-size: 16px;")
        self.minimize_button.clicked.connect(self.minimize_to_systray)  # Mise à jour ici
        
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.minimize_button)

        layout.addLayout(title_bar)

        # Champ pour entrer le nom du PC
        self.pc_label = QLabel("🧑‍💻 Nom du PC:")
        self.pc_label.setFont(QFont("Arial", 12))
        self.pc_entry = QLineEdit()
        self.pc_entry.setStyleSheet("background-color: #333333; color: white; padding: 5px;")
        layout.addWidget(self.pc_label)
        layout.addWidget(self.pc_entry)

        self.command_executor = LogSignalEmitter(self.pc_entry)
        layout.addWidget(self.command_executor)

        self.setLayout(layout)

         # Position en bas à droite
        self.position_above_taskbar()
      

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Ajout de l'icône dans la barre de notification (systray)
        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join(base_dir, "logo", "RCM.ico")), self)  # Remplace "icon.png" par ton icône
        self.tray_icon.setToolTip("ScanApp - En arrière-plan")
        
        # Création du menu du systray
        self.tray_menu = QMenu()
        restore_action = QAction("Restaurer", self)
        restore_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(restore_action)

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_systray_icon_click)
        self.tray_icon.show()

   def position_above_taskbar(self):
            """Place la fenêtre juste au-dessus de la barre des tâches."""
            screen_geometry = QApplication.desktop().screenGeometry()  # Taille totale de l'écran
            available_geometry = QApplication.desktop().availableGeometry()  # Zone dispo sans la barre des tâches

            # Calcul de la hauteur de la barre des tâches
            taskbar_height = screen_geometry.height() - available_geometry.height()

            # Positionnement de la fenêtre au-dessus de la barre des tâches
            self.move(screen_geometry.width() - self.width() - 10, available_geometry.height() - self.height() - 70 + taskbar_height)

   def minimize_to_systray(self):
        """Réduit l'application dans le systray au lieu de l'afficher à l'écran."""
        self.hide()
        self.tray_icon.showMessage("ScanApp", "L'application tourne en arrière-plan.", QSystemTrayIcon.Information, 2000)

   def show_window(self):
        """Restaure la fenêtre depuis le systray."""
        self.showNormal()
        self.activateWindow()

   def on_systray_icon_click(self, reason):
        """Gère le clic sur l'icône du systray."""
        if reason == QSystemTrayIcon.Trigger:  # Clic gauche
            self.show_window()

   def quit_application(self):
        """Quitte l'application proprement."""
        self.tray_icon.hide()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScanApp()
    window.show()
    sys.exit(app.exec())