#!/usr/bin/env python3
"""
📊 أداة تشخيصية لتحديد مشاكل إضافة المتدربين على Railway
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# إعدادات قاعدة البيانات
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

print("=" * 60)
print("🔍 تشخيص مشكلة إضافة المتدربين على Railway")
print("=" * 60)

# 1. التحقق من متغيرات البيئة
print("\n✅ التحقق من متغيرات البيئة:")
print(f"   DB_NAME: {'✓' if DB_NAME else '✗'}")
print(f"   DB_USER: {'✓' if DB_USER else '✗'}")
print(f"   DB_PASSWORD: {'✓' if DB_PASSWORD else '✗'}")
print(f"   DB_HOST: {'✓' if DB_HOST else '✗'}")
print(f"   DB_PORT: {'✓' if DB_PORT else '✗'}")

if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    print("\n❌ متغيرات البيئة غير كاملة!")
    sys.exit(1)

# 2. التحقق من ملف Excel
print("\n✅ التحقق من ملف Excel:")
excel_file = 'used_tables_export.xlsx'
if os.path.exists(excel_file):
    print(f"   ✓ ملف Excel موجود: {excel_file}")
else:
    print(f"   ✗ ملف Excel غير موجود: {excel_file}")
    print("   ← هذا قد يكون السبب الرئيسي للمشكلة على Railway")

# 3. الاتصال بقاعدة البيانات
print("\n✅ اختبار الاتصال بقاعدة البيانات:")
try:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    connection = engine.connect()
    print("   ✓ تم الاتصال بنجاح")
    
    # 4. التحقق من وجود جدول sf01
    print("\n✅ التحقق من وجود جدول sf01:")
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'sf01'
        )
    """)).scalar()
    
    if result:
        print("   ✓ جدول sf01 موجود")
        
        # 5. التحقق من عدد الصفوف في sf01
        count = connection.execute(text("SELECT COUNT(*) FROM sf01")).scalar()
        print(f"   ✓ عدد المتدربين في sf01: {count}")
        
        if count == 0:
            print("   ⚠️  تحذير: جدول sf01 فارغ!")
            print("   → قد تحتاج إلى تحميل البيانات من Excel أولاً")
        
        # 6. عرض أول 5 متدربين
        print("\n✅ أول 5 متدربين في sf01:")
        students = connection.execute(text("""
            SELECT student_id, "student_Name", "Major" FROM sf01 LIMIT 5
        """)).fetchall()
        
        if students:
            for student in students:
                print(f"   - {student[0]}: {student[1]} ({student[2]})")
        else:
            print("   ✗ لا توجد بيانات")
    else:
        print("   ✗ جدول sf01 غير موجود!")
        print("   → قد تحتاج إلى إنشاء الجدول أولاً")
    
    # 7. التحقق من وجود جدول course_enrollments
    print("\n✅ التحقق من وجود جدول course_enrollments:")
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'course_enrollments'
        )
    """)).scalar()
    
    if result:
        print("   ✓ جدول course_enrollments موجود")
        count = connection.execute(text("SELECT COUNT(*) FROM course_enrollments")).scalar()
        print(f"   ✓ عدد التسجيلات: {count}")
    else:
        print("   ✗ جدول course_enrollments غير موجود!")
    
    # 8. التحقق من UNIQUE CONSTRAINT
    print("\n✅ التحقق من القيود:")
    constraints = connection.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = 'course_enrollments'
    """)).fetchall()
    
    if constraints:
        for constraint in constraints:
            print(f"   - {constraint[0]} ({constraint[1]})")
    else:
        print("   ✗ لا توجد قيود!")
    
    connection.close()
    
except Exception as e:
    print(f"   ✗ فشل الاتصال: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ التشخيص اكتمل")
print("=" * 60)

print("\n📝 التوصيات:")
if not os.path.exists(excel_file):
    print("1. ❌ ملف Excel غير موجود على Railway")
    print("   → الحل: تم تعديل الكود ليبحث عن البيانات من قاعدة البيانات أولاً")
    print("   → للتحقق: تأكد من وجود البيانات في جدول sf01")

if count == 0:
    print("2. ⚠️  جدول sf01 فارغ")
    print("   → الحل: قم بتحميل البيانات من Excel أو من مصدر آخر")

print("\n💡 للمزيد من المعلومات:")
print("   - تحقق من ملفات السجلات (logs) على Railway")
print("   - تأكد من أن متغيرات البيئة محدثة بشكل صحيح")
print("   - جرب إضافة متدرب برقم موجود بالفعل في sf01")
