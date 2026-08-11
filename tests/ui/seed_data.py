from emp.models import Emp

Emp.objects.all().delete()

Emp.objects.create(
    name="John Doe",
    emp_id="EMP001",
    phone="9999999991",
    address="Pune",
    working=True,
    department="CSE",
)
Emp.objects.create(
    name="johnson smith",
    emp_id="EMP002",
    phone="9999999992",
    address="Mumbai",
    working=False,
    department="ME",
)
Emp.objects.create(
    name="Alice Johnson",
    emp_id="EMP003",
    phone="9999999993",
    address="Bengaluru",
    working=True,
    department="EE",
)
Emp.objects.create(
    name="Marie-Claire",
    emp_id="EMP004",
    phone="9999999994",
    address="Delhi",
    working=True,
    department="ME",
)
Emp.objects.create(
    name="O'Connor Liam",
    emp_id="EMP005",
    phone="9999999995",
    address="Chennai",
    working=False,
    department="CSE",
)
Emp.objects.create(
    name="José Alvarez",
    emp_id="EMP006",
    phone="9999999996",
    address="Hyderabad",
    working=True,
    department="EE",
)
