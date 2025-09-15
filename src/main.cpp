#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickItem>

#include "appconfig.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    QQmlApplicationEngine engine;

    AppConfig *appConfig = AppConfig::instance();
    appConfig->setVersion(QString("0.1"));

    engine.loadFromModule("pillcounter", "Main");

    if (engine.rootObjects().isEmpty()) {
        return -1;
    }

    return app.exec();
}
