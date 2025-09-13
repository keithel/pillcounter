import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dial {
    id: dial
    property string name: ""
    property alias displayValue: valueText.text
    font: label.font
    KeyNavigation.tab: morphCloseCheckbox
    ColumnLayout {
        anchors.centerIn: parent
        Text {
            id: label
            Layout.alignment: Qt.AlignHCenter
            text: dial.name
            font.pixelSize: 9
        }
        Text {
            id: valueText
            Layout.alignment: Qt.AlignHCenter
            text: dial.value
            font: dial.font
        }
    }
}