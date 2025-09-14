import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import io.qt.dev
import Qt.labs.platform

ApplicationWindow {
    id: window
    visible: true
    width: 1024
    height: 768

    onClosing: function (close) {
        pillCounter.quit()
    }

    Component.onCompleted: {
        pillCounter.activate()
        // We only have one view now, the annotated result
        imagePathPrefix = "orig_"
        image.source = Qt.binding(function() { return "image://cv/" + imagePathPrefix + imagePath + "?count=" + pillCounter.image_count; } )
    }

    title: qsTr("Pill Counter")

    property real buttonFontPixelSize: (window.width <= 640) ? 18 : 27
    property real textFontPixelSize: (window.width <= 640) ? 18 : 27
    property string imagePathPrefix: ""
    property alias imagePath: pillCounter.image_path
    property alias pillCount: pillCounter.pill_count
    property alias imageFormat: pillCounter.image_format

    PillCounter {
        id: pillCounter
        // --- REMOVED bindings to the old dials and checkboxes ---
    }

    // --- REMOVED header toolbar as it's no longer needed ---

    Item {
        id: windowContent
        anchors.fill: parent
        anchors.margins: 10

        Image {
            id: image
            fillMode: Image.PreserveAspectFit
            anchors.fill: parent
            anchors.bottomMargin: 100 // Leave space for the text and quit button

            focus: true
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
                text: pillCount >= 0 ? "Detected "
                      + pillCount + " pills." : "Initializing AI Model..."
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                // --- REMOVED all LabeledDial and CheckBox controls ---

                Button {
                    id: quitButton
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
