# Lab 3: Create text2sql_agent 
This lab we will import text2sql agent that connect to openapi tool that is used to query database

### Prerequisites
- Complete Lab_0 (setup the lab environment).
- Have the `orchestrate` CLI installed and configured.
- complete LAB_1 to activate orchestrate environment. If not, run the following command

```
orchestrate env list
orchestrate env activate trial-env -a <YOUR_API_KEY>
```

## 2 — Import the agent and tools

1. cd to this directory: `LAB_3_TEXT2SQL_AGENT/text2sql_agent`
2. Import the tool and agent into watsonX Orchestrate using bash script. Run the following function

```
bash import-all.sh
```
or
```
orchestrate tools import -k openapi -f tool/openai_query_db.json
orchestrate agents import -f agent/st_gabriel_text2sql_agent.yaml
```



## example questions:

**STUDENT INFORMATION** 
- นักเรียนที่มาจากจังหวัดเชียงใหม่มีกี่คนและแบ่งตามระดับชั้นเรียนอย่างไร
- นักเรียนในแต่ละอำเภอของจังหวัดเชียงใหม่มีจำนวนเท่าไหร่
- นักเรียนที่อยู่อำเภอเมืองเชียงใหม่มีพ่อทำอาชีพอะไรบ้าง
- สัดส่วนสถานะภาพครอบครัวของนักเรียนทั้งหมดเป็นเปอร์เซ็นต์เท่าไหร่
- นักเรียนที่มีพ่อทำอาชีพเกี่ยวกับราชการและอยู่กรุงเทพมีใครบ้างและอยู่ชั้นไหน

**SCORING AND GRADE INFORMATION**
- นักเรียนที่มีคะแนนต่ำกว่า 50 เปอร์เซ็นต์ในวิชาไหนมีจำนวนมากที่สุด
- นักเรียนคนไหนมีคะแนนเฉลี่ยต่ำที่สุดในปีการศึกษา 2021
<!-- - วิชาที่นักเรียนได้เกรด F มากที่สุดคือวิชาอะไร -->
- นักเรียนที่ได้คะแนนต่ำกว่า 60 เปอร์เซ็นต์ในมากกว่า 3 วิชามีกี่คน

- วิชาไหนมีคะแนนเฉลี่ยสูงที่สุดและต่ำที่สุด

**ATTENDANCE INFORMATION**
- นักเรียนที่ขาดเรียนมากกว่า 10 วันในปีการศึกษา 2020 มีกี่คน
- สถิติการมาสายของนักเรียนในแต่ละเดือนของปีการศึกษา 2021
- เปอร์เซ็นต์การขาดเรียน ลาป่วย และมาสายของนักเรียนทั้งหมด

- นักเรียนที่ไม่เคยขาดเรียนในปีการศึกษา 2024 มีกี่คน


**LIBRARY ENTRY INFORMATION**
- นักเรียนคนไหนเข้าห้องสมุดบ่อยที่สุดในปี 2023
- แต่ละระดับชั้นมีนักเรียนเข้าห้องสมุดเฉลี่ยกี่คนต่อเดือน
- ห้องสมุดมีผู้ใช้บริการมากที่สุดในช่วงเวลาไหนของวัน
- เดือนไหนมีการใช้บริการห้องสมุดมากที่สุด
- นักเรียนที่ไม่เคยเข้าห้องสมุดเลยมีกี่คนแบ่งตามชั้นเรียน


**MINIMART, CANTEEN and ONLINE GOODS BUYING**
- นักเรียนชอบซื้ออาหารหรือขนมประเภทไหนมากที่สุด3อันดับในโรงอาหาร
- นักเรียนซื้ออาหารมากแค่ไหนเทียบกับขนม
- นักเรียนซื้ออาหารจากที่ไหนมากที่สุด
- นักเรียนซื้ออาหารจากที่ไหนเท่าไหร่บ้างในปี2025
- การซื้ออุปกรณ์เครื่องเขียนในแต่ละเดือนมีแนวโน้มเพิ่มขึ้นหรือลดลง

**FIRST AID ROOM INFORMATION**
- นักเรียนที่มาใช้บริการห้องพยาบาลด้วยอาการแผลมีกี่เปอร์เซ็นต์ของการมาใช้บริการทั้งหม
- นักเรียนมีอาการปวดท้องมากี่เปอร์เซ็นต์ของการมาใช้บริการทั้งหมด
- มีนักเรียนเข้าห้องพยาบาลเพราะได้รับบาดเจ็บจากสถานที่ไหนมากที่สุด
- เดือนไหนมีการใช้บริการห้องพยาบาลมากที่สุด
- นักเรียนคนไหนมาใช้บริการห้องพยาบาลบ่อยที่สุดและมีอาการอะไรบ้าง