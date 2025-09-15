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
        imagePathPrefix = "annotated_"
        image.source = Qt.binding(function() {
            return pillCounter.live_image_count ? "image://cv/" + imagePathPrefix + imagePath + "?count=" + pillCounter.live_image_count : ""
        } )
    }

    title: qsTr("Pill Counter (AI-Powered)")

    property real buttonFontPixelSize: 20
    property real textFontPixelSize: 22
    property string imagePathPrefix: ""
    property alias imagePath: pillCounter.image_path
    property alias pillCount: pillCounter.pill_count
    property bool imageMode: false

    PillCounter {
        id: pillCounter
        onImage_files_loaded: function(loaded) {
            imageMode = loaded
        }
        confidence_threshold: confidenceDial.value / 100.0
        // --- NEW: Bind font size to the new dial ---
        font_size: fontDial.value / 10.0
    }

    FileDialog {
        id: fileDialog
        title: "Please choose one or more images"
        fileMode: FileDialog.OpenFiles
        nameFilters: [ "Image files (*.jpg *.jpeg *.png)" ]
        onAccepted: {
            pillCounter.loadImageFiles(fileDialog.files)
        }
        onRejected: {
            pillCounter.setLiveMode(true)
        }
    }

    ColumnLayout {
        id: windowContent
        anchors.fill: parent
        anchors.margins: 10

        Image {
            id: image
            fillMode: Image.PreserveAspectFit
            Layout.fillWidth: true
            Layout.fillHeight: true

            MouseArea {
                anchors.fill: parent
                onPressed: { imagePathPrefix = "unannotated_" }
                onReleased: { imagePathPrefix = "annotated_" }
                onCanceled: { imagePathPrefix = "annotated_" }
            }
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
                onClicked: {
                    pillCounter.setLiveMode(false)
                    fileDialog.open()
                }
            }

            Button {
                text: "Live Mode"
                font.pixelSize: buttonFontPixelSize
                onClicked: pillCounter.setLiveMode(true)
                highlighted: !imageMode
            }

            LabeledDial {
                id: confidenceDial
                name: "Confidence"
                from: 0
                to: 100
                stepSize: 1
                value: 49
                displayValue: value + "%"

                Component.onCompleted: increase();

                Connections {
                    function onValueChanged() {
                        if (imageMode)
                            pillCounter.processCurrentImage()
                    }
                }
            }

            // --- NEW: Font Size Dial ---
            LabeledDial {
                id: fontDial
                name: "Font Size"
                from: 2
                to: 10 // from 0.1 to 1.0
                stepSize: 1
                value: 2 // Default to 0.3
                displayValue: value / 10.0

                Component.onCompleted: increase()

                Connections {
                    function onValueChanged() {
                        if (imageMode)
                            pillCounter.processCurrentImage()
                    }
                }
            }
            // --- End of new section ---

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
                enabled: pillCounter.current_image_index < pillCounter.static_image_count-1
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
