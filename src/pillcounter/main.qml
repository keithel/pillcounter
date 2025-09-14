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
        // --- MODIFIED: Start with the "annotated_" prefix ---
        imagePathPrefix = "annotated_"
        image.source = Qt.binding(function() { return "image://cv/" + imagePathPrefix + imagePath + "?count=" + pillCounter.image_count; } )
    }

    title: qsTr("Pill Counter (AI-Powered)")

    property real buttonFontPixelSize: 20
    property real textFontPixelSize: 22
    property string imagePathPrefix: ""
    property alias imagePath: pillCounter.image_path
    property alias pillCount: pillCounter.pill_count
    property alias imageFormat: pillCounter.image_format
    property bool imageMode: false

    PillCounter {
        id: pillCounter
        onImage_files_loaded: function(loaded) {
            imageMode = loaded
        }
    }

    FileDialog {
        id: fileDialog
        title: "Please choose one or more images"
        fileMode: FileDialog.OpenFiles
        nameFilters: [ "Image files (*.jpg *.jpeg *.png)" ]
        onAccepted: {
            pillCounter.loadImageFiles(fileDialog.files)
        }
    }

    Item {
        id: windowContent
        anchors.fill: parent
        anchors.margins: 10

        Image {
            id: image
            fillMode: Image.PreserveAspectFit
            anchors.fill: parent
            anchors.bottomMargin: 120

            // --- NEW: MouseArea to toggle view ---
            MouseArea {
                anchors.fill: parent
                onPressed: {
                    // When pressed, switch to the unannotated image
                    imagePathPrefix = "unannotated_"
                }
                onReleased: {
                    // When released, switch back to the annotated image
                    imagePathPrefix = "annotated_"
                }
                onCanceled: {
                    // Also switch back if the press is canceled
                    imagePathPrefix = "annotated_"
                }
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
                text: {
                    if (pillCount >= 0) {
                        if (imageMode) {
                            return "Image " + (pillCounter.current_image_index + 1) + ": Detected " + pillCount + " pills."
                        } else {
                            return "Live Mode: Detected " + pillCount + " pills."
                        }
                    } else {
                        return "Initializing AI Model..."
                    }
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: 15

                Button {
                    text: "Open Image(s)"
                    font.pixelSize: buttonFontPixelSize
                    onClicked: fileDialog.open()
                }

                Button {
                    text: "Live Mode"
                    font.pixelSize: buttonFontPixelSize
                    onClicked: pillCounter.setLiveMode()
                    highlighted: !imageMode
                }

                Button {
                    id: prevButton
                    text: "< Prev"
                    font.pixelSize: buttonFontPixelSize
                    visible: imageMode
                    enabled: pillCounter.current_image_index > 0
                    onClicked: pillCounter.previousImage()
                }

                Button {
                    id: nextButton
                    text: "Next >"
                    font.pixelSize: buttonFontPixelSize
                    visible: imageMode
                    onClicked: pillCounter.nextImage()
                }

                Item { Layout.fillWidth: true }

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
        ScriptAction { script: Qt.quit(); }
    }
}
