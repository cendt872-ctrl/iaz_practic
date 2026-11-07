import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_iaz_xml(filename="unit_resources_report.xml"):
    # Створюємо кореневий елемент документа
    root = ET.Element("IAZ_Report", date="2026-11-07", classification="Службова інформація")

    # 1. Блок інформації про підрозділ (Базове завдання: назва, кількість, стан)
    units_section = ET.SubElement(root, "Units")
    
    units_data = [
        {"name": "1-й механізований батальйон", "personnel_count": "420", "status": "Боєздатний"},
        {"name": "Дивізіон ППО", "personnel_count": "145", "status": "Боєздатний (на чергуванні)"},
        {"name": "Ремонтно-відновлювальний батальйон", "personnel_count": "210", "status": "Виконує завдання"}
    ]

    for u in units_data:
        unit_elem = ET.SubElement(units_section, "Unit")
        ET.SubElement(unit_elem, "Name").text = u["name"]
        ET.SubElement(unit_elem, "Quantity").text = u["personnel_count"]
        ET.SubElement(unit_elem, "Status").text = u["status"]

    # 2. Блок даних про ресурси, транспорт та обладнання (Варіант 4: кількість та доступність)
    resources_section = ET.SubElement(root, "Resources")

    resources_data = [
        {"type": "Бронетехніка (БМП/БТР)", "quantity": "32", "available": "28", "readiness": "87.5%"},
        {"type": "Вантажні автомобілі логістики", "quantity": "45", "available": "41", "readiness": "91.1%"},
        {"type": "Комплекси БпЛА розвідувальні", "quantity": "18", "available": "18", "readiness": "100%"},
        {"type": "Термінали супутникового зв'язку", "quantity": "25", "available": "24", "readiness": "96.0%"}
    ]

    for r in resources_data:
        res_elem = ET.SubElement(resources_section, "Resource")
        ET.SubElement(res_elem, "EquipmentName").text = r["type"]
        ET.SubElement(res_elem, "TotalQuantity").text = r["quantity"]
        ET.SubElement(res_elem, "AvailableQuantity").text = r["available"]
        ET.SubElement(res_elem, "AvailabilityRate").text = r["readiness"]

    # Форматуємо XML з красивими відступами (pretty print)
    raw_xml = ET.tostring(root, encoding="utf-8")
    parsed_xml = minidom.parseString(raw_xml)
    pretty_xml = parsed_xml.toprettyxml(indent="    ", encoding="utf-8")

    with open(filename, "wb") as f:
        f.write(pretty_xml)

    print(f"✔ XML-файл успішно створено: {filename}")

if __name__ == "__main__":
    generate_iaz_xml()