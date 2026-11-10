# Mini guideline — bài làm cá nhân

> Điền nội dung này trước khi bắt đầu gán nhãn. Giữ lại các quyết định sau khi self-QC.

## Định nghĩa lớp

| Lớp | Định nghĩa của bạn | Ví dụ/điểm phân biệt |
| --- | --- | --- |
| `car` | ID 0. Xe bốn bánh cỡ nhỏ chở người: sedan, hatchback, SUV, taxi, xe bán tải (pickup). | Thân thấp, có nắp capo rõ, phần sau là cốp hoặc thùng hở nhỏ. Xe bán tải vẫn là `car` dù có thùng chở hàng. Không gán cho mô tô, xe đạp. |
| `truck` | ID 1. Xe chuyên chở hàng: xe tải thùng kín hoặc thùng hở, xe ben, xe bồn, xe đầu kéo (có hoặc không có rơ-moóc). | Cabin tách rời khỏi thùng hàng, thùng hàng thường cao và dài hơn cabin. Xe bán tải cabin nhỏ thuộc `car`. Xe thân liền khối (cabin và khoang sau chung một hộp) thuộc `van`. |
| `bus` | ID 2. Xe chở khách nhiều hàng ghế: xe buýt thành phố, xe khách, minibus chở khách. | Thân dài hình hộp, dãy cửa sổ hành khách chạy dọc thân, cửa lên xuống lớn. Dài rõ rệt so với van. Van chở người cỡ nhỏ thuộc `van`. |
| `van` | ID 3. Xe van/minivan thân liền khối, chở hàng hoặc chở người. | Mũi xe ngắn, nóc cao hơn `car`, phần đuôi gần thẳng đứng, kích thước nhỏ hơn `bus`. SUV vẫn là `car`; MPV/minivan thân hộp là `van`. |

## Quy tắc chung

- Box bám sát vật thể nghĩa là: 4 cạnh chạm điểm ngoài cùng của phần thân xe nhìn thấy được, gồm cả bánh xe; không lấy bóng đổ, mặt đường, trời hoặc xe bên cạnh. Mỗi xe một box riêng, kể cả xe cùng lớp đứng sát nhau; không gộp hai xe vào một box.
- Vật thể bị che khuất: vẽ box quanh phần nhìn thấy được, không đoán phần bị che. Vẫn gán nếu phần nhìn thấy đủ để nhận ra lớp. Hai xe chồng nhau thì mỗi xe một box trên phần nhìn thấy của chính nó.
- Vật thể bị cắt bởi rìa ảnh: kéo cạnh box chạm đúng rìa ảnh, không đoán phần nằm ngoài khung. Gán nếu phần trong khung đủ để nhận ra lớp.
- Vật thể rất nhỏ/mơ hồ: xe ở xa vẫn gán nếu phóng to còn nhận ra là xe và xác định được lớp. Nếu chỉ còn vài pixel hoặc mảnh nhỏ không xác định chắc lớp thì không tự đoán, ghi tên ảnh vào bảng dưới và hỏi giảng viên. Không gán người, xe đạp, mô tô/xe máy, biển báo, xe trên bảng quảng cáo hoặc hình phản chiếu.

## Ghi lại quyết định cho ít nhất ba ca mơ hồ

| Ảnh | Tình huống | Quyết định cuối | Lý do theo schema |
| --- | --- | --- | --- |
| `drive_019` | Minivan/MPV chở người, thân hộp, nóc cao, dễ nhầm với `car`. | `van` . | Schema xếp minivan chở người vào `van`; xe có thân liền khối và nóc cao, khác sedan/SUV của `car`. |
| `drive_007` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |
| `drive_003` | Xe bị cắt bởi rìa ảnh, chỉ còn đầu xe trong khung. | `truck`. | Quy tắc chung về vật thể bị cắt khung. |
| `drive_011` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |
| `drive_012` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |
| `drive_014` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |
| `drive_030` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |
| `drive_031` | Xe rất nhỏ ở xa, trong vùng tối, không xác định chắc lớp. | Không gán, đã hỏi giảng viên. | Quy tắc chung: không tự đoán lớp khi không nhận diện được. |

