import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import io.qt.dev

ApplicationWindow {
    id: window
    visible: true
    width: 640
    height: 480

    Component.onCompleted: {
        pillCounter.activate()
        imagePath = "pills1.jpg"
        image.source = Qt.binding(function() { return "image://cv/" + imagePath + "?count=" + pillCounter.image_count; } )
    }

    title: qsTr("Pill Counter")

    property real buttonFontPixelSize: (window.width <= 640) ? 18 : 27
    property real textFontPixelSize: (window.width <= 640) ? 18 : 27
    property string imagePath: ""
    property alias pillCount: pillCounter.pill_count
    property alias imageFormat: pillCounter.image_format

    PillCounter {
        id: pillCounter
        image_path: imagePath
        hue_low: hueLowSlider.value
        hue_high: hueHighSlider.value
        saturation_low: saturationLowSlider.value
        saturation_high: saturationHighSlider.value
        value_low: valueLowSlider.value
        value_high: valueHighSlider.value
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
                id: image
                anchors.fill: parent
                anchors.margins: 10
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
                Label {
                    text: "H"
                }
                ColumnLayout {
                    Slider {
                        id: hueLowSlider
                        from: 0
                        to: 180
                        stepSize: 1
                        value: 0
                    }
                    Slider {
                        id: hueHighSlider
                        from: 0
                        to: 180
                        stepSize: 1
                        value: 180
                    }
                }
                Label {
                    text: "S"
                }
                ColumnLayout {
                    Slider {
                        id: saturationLowSlider
                        from: 0
                        to: 255
                        stepSize: 1
                        value: 1  // 0
                    }
                    Slider {
                        id: saturationHighSlider
                        from: 0
                        to: 255
                        stepSize: 1
                        value: 39  // 50
                    }
                }
                Label {
                    text: "V"
                }
                ColumnLayout {
                    Slider {
                        id: valueLowSlider
                        from: 0
                        to: 255
                        stepSize: 1
                        value: 200  // 160
                    }
                    Slider {
                        id: valueHighSlider
                        from: 0
                        to: 255
                        stepSize: 1
                        value: 255
                    }
                }

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
