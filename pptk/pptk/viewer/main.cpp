#include <QApplication>
#include <QDebug>
#include <iostream>
#include "viewer.h"
//#include "design.h"

#include <QWindow>
#include <QPushButton>
#include <QLayout>
#include <string>
#include <QWidget>
#include <QTextEdit>

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        qDebug() << "usage: viewer <port number>";
        return 1;
    }
    QApplication a(argc, argv);
    unsigned short clientPort = (unsigned short)atoi(argv[1]);
//    unsigned short clientPort = 12345;

    Viewer viewer(clientPort);
    viewer.create();
    viewer.show();
    usleep(5000);
  //  Design design(viewer.winId(),viewer.serverPort);

    return a.exec();
}
