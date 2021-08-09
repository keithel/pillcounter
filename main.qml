import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import io.qt.dev

ApplicationWindow {
    id: window
    visible: true
    width: 640
    height: 480
//    flags: Qt.FramelessWindowHint
//    visibility: "Maximized"

    title: qsTr("Pill Counter")

    property real buttonFontPixelSize: (window.width <= 640) ? 18 : 27
    property real textFontPixelSize: (window.width <= 640) ? 18 : 27
    property string imagePath: "pills1.jpg"
    property alias pillCount: pillCounter.pill_count
    property alias imageFormat: pillCounter.image_format

    PillCounter {
        id: pillCounter
        image_path: imagePath
    }

    Item {
        id: windowContent
        anchors.fill: parent
        anchors.margins: 10

        Rectangle {
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                bottom: descriptionAndButsLayout.top
            }
            color: "transparent"

            Image {
                anchors.fill: parent
                anchors.margins: 10

                source: "image://cv/" + imagePath + "?count=" + pillCounter.image_count
            }
        }

        ColumnLayout {
            id: descriptionAndButsLayout
            anchors {
                bottom: parent.bottom
                left: parent.left
                right: parent.right
            }

            Text {
                Layout.bottomMargin: 20
                font.pixelSize: textFontPixelSize
                text: "Image format: " + imageFormat
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                Layout.bottomMargin: 20
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: textFontPixelSize
                text: pillCount >= 0 ? "There are "
                      + pillCount + " pills in the image." : ""
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Button {
//                    background: Item {}
                    text: "Quit"
                    font.pixelSize: buttonFontPixelSize
                    onClicked: quitAnim.start()
                }
            }
        }
    }

    SequentialAnimation {
        id: quitAnim

        NumberAnimation {
            to: 0
            duration: 300
            target: windowContent
            property: "scale"
            easing.type: Easing.InCubic
        }
        ScriptAction {
            script: Qt.quit();
        }
    }
}
