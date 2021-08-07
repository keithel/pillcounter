//import QtQuick
//import QtQuick.Window

//Window {
//    width: 640
//    height: 480
//    visible: true
//    title: qsTr("Hello World")
//}

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 640
    height: 480
//    flags: Qt.FramelessWindowHint
//    visibility: "Maximized"

    title: qsTr("Pill Counter")

    property int pillCount: -1
    property real buttonFontPixelSize: (window.width <= 640) ? 18 : 27
    property real textFontPixelSize: (window.width <= 640) ? 18 : 27

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

                source: "image://cv/pills1.jpg"
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
