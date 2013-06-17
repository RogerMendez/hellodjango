from django.shortcuts import render_to_response, get_object_or_404

from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from personal.models import Empleados
from datetime import datetime

@dajaxice_register
def employee(request, carnet):
    dajax = Dajax()
    empleado = Empleados.objects.get(ci=carnet)
    nombre = empleado.nombre
    paterno = empleado.paterno
    materno = empleado.materno
    direccion = empleado.direccion
    telefono = empleado.telefono
    email = empleado.email
    nac = empleado.fecha_nac
    civil = empleado.estado_civil
    sexo = empleado.sexo
    fecha_nac = nac.strftime("%d/%m/%Y")
    profe = empleado.profesion_id
    dajax.assign('#id_nombre','value',str(nombre))
    dajax.assign('#id_paterno','value',str(paterno))
    dajax.assign('#id_materno','value',str(materno))
    dajax.assign('#id_direccion','value',str(direccion))
    dajax.assign('#id_telefono','value',str(telefono))
    dajax.assign('#id_email','value',str(email))
    dajax.assign('#id_fecha_nac','value',str(fecha_nac))
    data = [
        {'civil':civil, 'sexo':sexo,'profesion':profe }]
    dajax.add_data(data,'seleccionar')
    #dajax.add_data(sexo,'sexo')
    #dajax.assign('#id_nombre','value',str(nombre))
    return dajax.json()


@dajaxice_register
def multiply(request, a, b):
    dajax = Dajax()
    result = int(a) * int(b)
    dajax.assign('#result','value',str(result))
    return dajax.json()