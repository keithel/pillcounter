import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import io.qt.dev

ApplicationWindow {
    id: window
    visible: true
    width: 640
    height: 480

    onClosing: function (close) {
        pillCounter.quit()
    }

    Component.onCompleted: {
        pillCounter.activate()
        imagePath = "pills1.jpg"
        imagePathPrefix = "3_"
        toolBarRowLayout.children[3].toggle()
        image.source = Qt.binding(function() { return "image://cv/" + imagePathPrefix + imagePath + "?count=" + pillCounter.image_count; } )
    }

    title: qsTr("Pill Counter")

    property real buttonFontPixelSize: (window.width <= 640) ? 18 : 27
    property real textFontPixelSize: (window.width <= 640) ? 18 : 27
    property string imagePathPrefix: ""
    property string imagePath: ""
    property alias pillCount: pillCounter.pill_count
    property alias imageFormat: pillCounter.image_format

    PillCounter {
        id: pillCounter
        image_path: imagePath
        gray_threshold: grayThresholdSlider.value
    }

    header: ToolBar {
        ButtonGroup {
            buttons: toolBarRowLayout.children
        }
        RowLayout {
            id: toolBarRowLayout
            anchors.fill: parent
            ToolButton {
                id: tborig
                checkable: true
                text: "original"
                onClicked: imagePathPrefix = "orig_"
            }
            Repeater {
                model: 4
                delegate: ToolButton {
                    checkable: true
                    text: "Step " + (modelData+1)
                    onClicked: imagePathPrefix = (modelData+1) + "_"
                }
            }
        }
    }

    Item {
        id: windowContent
        anchors.fill: parent
        anchors.margins: 10

        Image {
            id: image
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                bottom: descriptionAndButsLayout.top
                margins: 10
            }
            focus: true
            KeyNavigation.tab: grayThresholdSlider
            Rectangle {
                anchors.fill: parent
                visible: parent.focus
                color: "transparent"
                border {
                    color: "blue"
                }
            }

            Keys.onPressed: function (event) {
                switch (event.key) {
                case Qt.Key_QuoteLeft:
                    imagePathPrefix = ""
                    event.accepted = true;
                    break;
                case Qt.Key_1:
                    imagePathPrefix = "orig_"
                    event.accepted = true;
                    break;
                case Qt.Key_2:
                    imagePathPrefix = "1_"
                    event.accepted = true;
                    break;
                case Qt.Key_3:
                    imagePathPrefix = "2_"
                    event.accepted = true;
                    break;
                case Qt.Key_4:
                    imagePathPrefix = "3_"
                    event.accepted = true;
                    break;
                case Qt.Key_5:
                    imagePathPrefix = "4_"
                    event.accepted = true;
                    break;
                default:
                    break;
                }
            }

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                onPressed: function (mouse) {
                    if (mouse.button == Qt.LeftButton)
                        imagePathPrefix = "orig_"
                    else
                        imagePathPrefix = "4_"
                }
                onReleased: imagePathPrefix = ""
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
                    text: "Gray Threshold"
                }
                Slider {
                    id: grayThresholdSlider
                    KeyNavigation.tab: quitButton
                    from: 0
                    to: 255
                    stepSize: 1
                    value: 192  // 200
                }

                Button {
                    id: quitButton
                    KeyNavigation.tab: image
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
