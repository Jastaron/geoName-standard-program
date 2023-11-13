from Controller import *

if __name__ == '__main__':
    # Create the application instance
    app = QApplication([])
    controller = SGNS_Controller()
    controller.show()
    app.exec_()