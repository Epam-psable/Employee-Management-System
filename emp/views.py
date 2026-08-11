from django.db import IntegrityError
from django.shortcuts import redirect, render

from .models import Emp


DUPLICATE_EMP_ID_ERROR = "Employee ID already exists. Please use a different ID."


def emp_home(request):
    q = request.GET.get("q", "").strip()

    if q:
        emps = Emp.objects.filter(name__icontains=q)
    else:
        emps = Emp.objects.all()

    total_employees = Emp.objects.count()
    active_employees = Emp.objects.filter(working=True).count()
    inactive_employees = Emp.objects.filter(working=False).count()

    return render(
        request,
        "emp/home.html",
        {
            'emps': emps,
            'q': q,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
        },
    )


def add_emp(request):
    if request.method == "POST":
        emp_name = (request.POST.get("emp_name") or "").strip()
        emp_id = (request.POST.get("emp_id") or "").strip()
        emp_phone = (request.POST.get("emp_phone") or "").strip()
        emp_address = (request.POST.get("emp_address") or "").strip()
        emp_working = request.POST.get("emp_working")
        emp_department = (request.POST.get("emp_department") or "").strip()

        if Emp.objects.filter(emp_id=emp_id).exists():
            return render(
                request,
                "emp/add_emp.html",
                {
                    "error": DUPLICATE_EMP_ID_ERROR,
                    "emp_name": emp_name,
                    "emp_id": emp_id,
                    "emp_phone": emp_phone,
                    "emp_address": emp_address,
                    "emp_working": emp_working,
                    "emp_department": emp_department,
                },
            )

        e = Emp(
            name=emp_name,
            emp_id=emp_id,
            phone=emp_phone,
            address=emp_address,
            department=emp_department,
            working=bool(emp_working),
        )
        try:
            e.save()
        except IntegrityError:
            return render(
                request,
                "emp/add_emp.html",
                {
                    "error": DUPLICATE_EMP_ID_ERROR,
                    "emp_name": emp_name,
                    "emp_id": emp_id,
                    "emp_phone": emp_phone,
                    "emp_address": emp_address,
                    "emp_working": emp_working,
                    "emp_department": emp_department,
                },
            )

        return redirect("/emp/home/")

    return render(request, "emp/add_emp.html", {})

def delete_emp(request,emp_id):
    emp=Emp.objects.get(pk=emp_id)
    emp.delete()
    return redirect("/emp/home/")

def update_emp(request, emp_id):
    emp = Emp.objects.get(pk=emp_id)
    return render(
        request,
        "emp/update_emp.html",
        {
            "emp": emp,
        },
    )

def do_update_emp(request, emp_id):
    if request.method == "POST":
        emp_name = (request.POST.get("emp_name") or "").strip()
        emp_id_temp = (request.POST.get("emp_id") or "").strip()
        emp_phone = (request.POST.get("emp_phone") or "").strip()
        emp_address = (request.POST.get("emp_address") or "").strip()
        emp_working = request.POST.get("emp_working")
        emp_department = (request.POST.get("emp_department") or "").strip()

        e = Emp.objects.get(pk=emp_id)

        if (
            Emp.objects.filter(emp_id=emp_id_temp)
            .exclude(pk=e.pk)
            .exists()
        ):
            attempted_emp = Emp(
                id=e.id,
                name=emp_name,
                emp_id=emp_id_temp,
                phone=emp_phone,
                address=emp_address,
                department=emp_department,
                working=bool(emp_working),
            )
            return render(
                request,
                "emp/update_emp.html",
                {
                    "emp": attempted_emp,
                    "error": DUPLICATE_EMP_ID_ERROR,
                },
            )

        e.name = emp_name
        e.emp_id = emp_id_temp
        e.phone = emp_phone
        e.address = emp_address
        e.department = emp_department
        e.working = bool(emp_working)

        try:
            e.save()
        except IntegrityError:
            attempted_emp = Emp(
                id=e.id,
                name=emp_name,
                emp_id=emp_id_temp,
                phone=emp_phone,
                address=emp_address,
                department=emp_department,
                working=bool(emp_working),
            )
            return render(
                request,
                "emp/update_emp.html",
                {
                    "emp": attempted_emp,
                    "error": DUPLICATE_EMP_ID_ERROR,
                },
            )

    return redirect("/emp/home/")
