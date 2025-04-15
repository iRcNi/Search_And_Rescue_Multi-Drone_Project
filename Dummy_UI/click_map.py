import sys
import folium
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create map with click JS
        self.setWindowTitle("Click to Get Coordinates")
        self.setGeometry(100, 100, 800, 600)

        map = folium.Map(location=[24.7136, 46.6753], zoom_start=6)

        click_js = """
            function addClickHandler(map) {
                map.on('click', function(e) {
                    var lat = e.latlng.lat.toFixed(6);
                    var lng = e.latlng.lng.toFixed(6);
                    alert("Coordinates: " + lat + ", " + lng);
                    console.log("Clicked coordinates: [" + lat + ", " + lng + "]");
                });
            }
        """
        from branca.element import Template, MacroElement
        template = Template(f"""
        <script>{click_js}</script>
        <script>
            addClickHandler({{this._parent.get_name()}});
        </script>
        """)
        macro = MacroElement()
        macro._template = template
        map.get_root().add_child(macro)

        map_file = "map.html"
        map.save(map_file)

        view = QWebEngineView()
        from PyQt5.QtCore import QUrl
        view.load(QUrl.fromLocalFile(os.path.abspath(map_file)))
        view.loadFinished.connect(lambda: print("Map loaded."))

        self.setCentralWidget(view)

app = QApplication(sys.argv)
window = MapWindow()
window.show()
sys.exit(app.exec_())
