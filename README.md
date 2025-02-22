# 🦄 Project Overview 🐱

The goal is to remotely execute magical terminal (cmd) commands on a desktop that belongs to an Active Directory (AD) kingdom. This is done using PsExec, a powerful tool from Microsoft's Sysinternals suite, allowing you to control remote machines as if you were a wizard riding a unicorn.

# 🦄 Key Features & Functionality 🐱

Send Terminal Commands Remotely

The app whispers commands to a remote machine in the Active Directory network.
The target machine is identified by its computer name (or perhaps its secret unicorn alias).
Using PsExec
Download here:
        https://download.sysinternals.com/files/PSTools.zip

The app harnesses the power of PsExec to run these commands remotely, without needing to log in manually.
Like a stealthy cat, PsExec executes commands in the background without drawing attention.
Capturing Output (stdout & stderr)

The app listens closely to the standard output (stdout) and error output (stderr).
Any result or error message from the command will appear on the app’s command screen, just like a curious cat watching a keyboard.
Minimizing to System Tray
# read the stderr and stdout flux in real time 
         for line in iter(self.current_process.stdout.readline, ''):
             self.log_signal.emit(line.strip())
                
        for error in iter(self.current_process.stderr.readline, ''):
            self.log_signal.emit(f"{error.strip()}")

There is a "Hide" button in the app.
Clicking it will make the app vanish like a unicorn into the system tray, running quietly in the background like a cat waiting for the perfect moment to strike.


![image](https://github.com/user-attachments/assets/90333efe-54c2-4281-975c-71cf253d117f)


# 🦄 Possible Use Cases 🐱
✨ Remote Administration – IT admins can run commands across multiple machines without ever leaving their castle.
✨ Troubleshooting – View mystical logs and errors remotely from the affected machine.
✨ Automation – Summon scripts or commands on multiple machines with a single command—like casting a spell.
