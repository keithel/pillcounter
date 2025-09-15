#include "appconfig.h"
#include <QtCore/QCoreApplication>
//#include <QCommandLineParser>

AppConfig::AppConfig(QObject *parent)
    : QObject{parent}
{
    // You can parse arguments here if you want config to be set from arguments.
    /*
    // I do know that QCoreApplication is around, as this is a QML singleton created by the qml
    // engine, which requires that the application be created before it is instantiated.
    qApp->arguments();

    QCommandLineParser parser;
    QCommandLineOption outFileOption(QStringList({"o", "output"}), "Output file", "outfile");
    parser.addOption(outFileOption);
    if(!parser.parse(qApp->arguments())) {
        qFatal() << "Failed to read command line arguments. aborting";
    }

    QString outFile = parser.value(outFileOption);
    if (!outFile.isEmpty()) {
        setOutputFile(outFile);
    }
    */
}

AppConfig *AppConfig::instance() {
    if (s_singletonInstance == nullptr)
        s_singletonInstance = new AppConfig(qApp);
    return s_singletonInstance;
}

AppConfig *AppConfig::create(QQmlEngine *, QJSEngine *engine)
{
    Q_ASSERT(s_singletonInstance);
    Q_ASSERT(engine->thread() == s_singletonInstance->thread());
    if (s_engine)
        Q_ASSERT(engine == s_engine);
    else
        s_engine = engine;

    QJSEngine::setObjectOwnership(s_singletonInstance, QJSEngine::CppOwnership);
    return s_singletonInstance;
}

QString AppConfig::version() const
{
    return m_version;
}

void AppConfig::setVersion(const QString &version)
{
    if (m_version != version) {
        m_version = version;
        emit versionChanged();
    }
}
