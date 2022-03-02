# Cuppa - Every cup is life


ระบบ Log-in /
หน้่า Profile / 
Edit Profile /
show my position /
show nearby cafe /





หัวข้อที่ต้องดึงมากจาก API
['geometry']['location'] --------lat,lng
['name']  ------string
['opening_hours']['open_now']  ------- boolean
['photos']  ----------link
['rating'] ----------int
['user_ratings_total'] ------------int
['vicinity'] ------string


geocoder ของ python มีปัญหา พิกัดไม่ตรงกับของ javascript ทำให้ยังไม่สามารถค้นหาจากพิกัดที่แน่นอนได้


เชื่อมต่อหน้าแผนที่กับหน้า cup near me เรียบร้อยแล้ว

DATE format เป็น yyyy-mm-mm