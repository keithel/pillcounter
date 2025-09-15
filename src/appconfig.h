#pragma once

#include <QObject>
#include <QQmlEngine>

class AppConfig : public QObject
{
    Q_OBJECT
    QML_SINGLETON
    QML_ELEMENT

    Q_PROPERTY(QString version READ version NOTIFY versionChanged)

public:
    explicit AppConfig(QObject *parent);
    ~AppConfig() = default;

    static AppConfig *instance();
    static AppConfig *create(QQmlEngine *, QJSEngine *engine);

    QString version() const;
    void setVersion(const QString &version);

signals:
    void versionChanged();

private:
    QString m_version;

    inline static AppConfig * s_singletonInstance = nullptr;
    inline static QJSEngine *s_engine = nullptr;
};
