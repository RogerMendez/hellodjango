#encoding:utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from organizacion.models import Unidades, Cargos
from personal.form import EmpleadoForm, ProfesionForm, Contrato, AsistenciaForm, ObservacionForm, PermisoForm
from personal.models import Empleados, contratacion, Asistencia, Entrada, Salida, Observacion, Permiso, moviidad

from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from datetime import datetime


@login_required(login_url='/user/login')
def home(request):
    return render_to_response('index_personal.html', context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def new_empleado(request, cod_cargo):
    if request.method == 'POST' :
        formulario = EmpleadoForm(request.POST, request.FILES)
        if formulario.is_valid() :
            carnet = formulario.cleaned_data['ci']
            nombre = formulario.cleaned_data['nombre']
            paterno = formulario.cleaned_data['paterno']
            email = formulario.cleaned_data['email']
            emple = Empleados.objects.filter(ci = carnet)
            if(emple):
                return HttpResponseRedirect('/contrato/new/'+str(carnet)+"/"+str(cod_cargo)+"/")
            else:
                newuser = User.objects.create_user(carnet, email, carnet)

                Empleados.objects.create(
                                        ci = carnet,
                                        nombre = nombre,
                                        email = email,
                                        paterno = paterno,
                                        materno = formulario.cleaned_data['materno'],
                                        direccion = formulario.cleaned_data['direccion'],
                                        telefono = formulario.cleaned_data['telefono'],
                                        estado_civil = formulario.cleaned_data['estado_civil'],
                                        sexo = formulario.cleaned_data['sexo'],
                                        fecha_nac = formulario.cleaned_data['fecha_nac'],
                                        foto = formulario.cleaned_data['foto'],
                                        profesion = formulario.cleaned_data['profesion'],
                                        usuario_id = newuser.id
                                    )
                newuser.is_active = 0
                newuser.first_name = nombre
                newuser.last_name = paterno
                newuser.save()
                #formulario.save()
                return HttpResponseRedirect('/contrato/new/'+str(carnet)+"/"+str(cod_cargo)+"/")
    else:
        formulario = EmpleadoForm()
    return render_to_response('personal/new_empleado.html', {'formulario' :formulario}, context_instance=RequestContext(request))

@login_required(login_url='/user/login')
def option_empleado(request):
    empleado=Empleados.objects.all()
    contratos = contratacion.objects.exclude(fecha_salida__lte = datetime.today())
    return render_to_response('personal/option_empleado.html', {'empleados' :empleado, 'contratos':contratos}, context_instance=RequestContext(request))

@login_required(login_url='/user/login')
def update_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleados, pk = empleado_id)
    if request.method == 'POST':
        formulario = EmpleadoForm(request.POST, instance = empleado)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/personal/option')
    else:
        formulario = EmpleadoForm(instance = empleado)
    return render_to_response('personal/update_empleado.html', {'formulario' :formulario}, context_instance=RequestContext(request))

@login_required(login_url='/user/login')
def new_profesion(request):
    if request.method == 'POST' :
        formulario = ProfesionForm(request.POST, request.FILES)
        if formulario.is_valid() :
            formulario.save()
            return HttpResponseRedirect('/personal')
    else:
        formulario = ProfesionForm()
    return render_to_response('personal/new_profesion.html', {'formulario' :formulario}, context_instance=RequestContext(request))

#CONTRATACION
@login_required(login_url='/user/login')
def cargos_contrato(request):
    unidad = Unidades.objects.all()
    cargo = Cargos.objects.all()
    return render_to_response('personal/cargo_contrato.html', {'cargos' :cargo, 'unidades' :unidad}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def contrato(request, empleado_ci, cargo_id):
    if request.method == 'POST' :
        formulario = Contrato(request.POST, request.FILES)
        if formulario.is_valid() :
            empleado = Empleados.objects.get(ci=int(empleado_ci))
            id =empleado.id
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin =formulario.cleaned_data['fecha_fin']
            sueldo=formulario.cleaned_data['sueldo']
            descuento=formulario.cleaned_data['descuento']
            cargo=int(cargo_id)
            contratacion.objects.create(fecha_entrada=fecha_inicio,
                                        fecha_salida=fecha_fin,
                                        estado='ACTIVO',
                                        sueldo=sueldo,
                                        descuento=descuento,
                                        empleado_id=id,
                                        cargo_id=cargo,
                                        )

            return HttpResponseRedirect('/personal')
    else:
        formulario = Contrato()
    return render_to_response('personal/new_contratacion.html', {'formulario' :formulario, 'empleado_ci':empleado_ci}, context_instance=RequestContext(request))


def new_asistencia(request):
    if request.method == 'POST' :
        formulario = AsistenciaForm(request.POST, request.FILES)
        if formulario.is_valid() :
            carnet = formulario.cleaned_data['ci']
            if Empleados.objects.filter(ci = carnet) :
                emple = Empleados.objects.get(ci = carnet)
                cod_emple = emple.id
                hoy = datetime.today()
                hora = hoy.strftime("%H:%M")
                if not Asistencia.objects.filter(empleado_id = emple.id, fecha = hoy) :
                    asis = Asistencia.objects.create(
                                                    fecha = hoy,
                                                    empleado_id = cod_emple
                                                    )
                else :
                    asis = Asistencia.objects.get(empleado_id = emple.id, fecha = hoy)
                #Modificar las Horas
                if hora >= "06:00" and hora <= "08:15" :
                    #Entrada mañana
                    entrada = Entrada.objects.create(
                                                    hora = hora,
                                                    obs = "MAÑANA",
                                                    asistencia = asis
                                                    )
                elif hora >= "13:00" and hora <= "14:15" :
                    #"Entrada Tarde"
                    entrada = Entrada.objects.create(
                                                    hora = hora,
                                                    obs = "TARDE",
                                                    asistencia = asis
                                                    )
                elif hora >= "12:00" and hora <= "12:59" :
                    #salida mañana
                    entrada = Salida.objects.create(
                                                    hora = hora,
                                                    obs = "MAÑANA",
                                                    asistencia = asis
                                                    )
                elif hora >= "18:00" and hora <= "22:00" :
                    #salida tarde
                    entrada = Salida.objects.create(
                                                    hora = hora,
                                                    obs = "TARDE",
                                                    asistencia = asis
                                                    )
                else:
                    if hora >= "08:16" and hora <= "11:59" :
                        #salida tarde
                        Entrada.objects.create(
                                            hora = hora,
                                            obs = "RETRASO",
                                            asistencia = asis
                                            )
                    if hora >= "14:16" and hora <= "17:59" :
                        #salida tarde
                        Entrada.objects.create(
                                            hora = hora,
                                            obs = "RETRASO",
                                            asistencia = asis
                                            )
                    if hora >= "22:01" and hora <= "05:59" :
                        #salida tarde
                        return HttpResponseRedirect('/personal/')
            else:
                return HttpResponseRedirect('/personal/asistencia/')
            return HttpResponseRedirect('/personal/asistencia/')
    else:
        formulario = AsistenciaForm()
    return  render_to_response('personal/new_asistencia.html', {'formulario' :formulario}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def new_observacion(request, cod_emple):
    if request.method == 'POST' :
        formulario = ObservacionForm(request.POST, request.FILES)
        if formulario.is_valid():

            Observacion.objects.create(
                                        tipo = formulario.cleaned_data['tipo'],
                                        descripcion = formulario.cleaned_data['descripcion'],
                                        fecha = datetime.today(),
                                        empleado_id = cod_emple,
                                        )
            #formulario.save()
            return HttpResponseRedirect('/personal/option')
    else:
        formulario = ObservacionForm()
    return  render_to_response('personal/new_observacion.html', {'formulario' :formulario}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def new_permiso(request, cod_emple):
    if request.method == 'POST' :
        formulario = PermisoForm(request.POST, request.FILES)
        if formulario.is_valid():
            Permiso.objects.create(
                                    descripcion = formulario.cleaned_data['descripcion'],
                                    fecha = datetime.today(),
                                    tiempo = formulario.cleaned_data['tiempo'],
                                    empleado_id = cod_emple,
                                   )
            return HttpResponseRedirect('/personal/option')
    else:
        formulario = PermisoForm()
    return  render_to_response('personal/new_observacion.html', {'formulario' :formulario}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def select_personal(request):
    empleado=Empleados.objects.all()
    contratos = contratacion.objects.exclude(fecha_salida__lte = datetime.today())
    return render_to_response('personal/cambio_personal.html', {'empleados' :empleado, 'contratos':contratos}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def cambio_cargo(request, empleado_cod):
    cargo = Cargos.objects.all()
    return render_to_response('personal/cargo_cambio.html', {'cargos' :cargo, 'empleado_cod' :empleado_cod}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def empleado_cambio(request, cargo_cod, empleado_cod):
    contrato = contratacion.objects.get(empleado_id = int(empleado_cod), estado = 'ACTIVO')
    moviidad.objects.create(
                            contrato_id = contrato.id,
                            cargo_id = int(cargo_cod),
                            fecha = datetime.today(),
                            )
    contrato.estado = 'INACTIVO'
    contratacion.objects.create(
                                fecha_entrada = datetime.today(),
                                fecha_salida = contrato.fecha_salida,
                                estado = 'ACTIVO',
                                sueldo = contrato.sueldo,
                                descuento = contrato.descuento,
                                empleado_id = contrato.empleado_id,
                                cargo_id = int(cargo_cod),
                                )
    contrato.save()
    return HttpResponseRedirect('/personal')



def ingresar(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/privado')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            #users = User.objects.get(username = usuario)
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/privado')
                else:
                    return render_to_response('user/noactivo.html', context_instance=RequestContext(request))
            else:
                return render_to_response('user/nousuario.html', context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('user/user_login.html',{'formulario':formulario}, context_instance=RequestContext(request))


@login_required(login_url='/user/login')
def privado(request) :
    usuario = request.user
    return render_to_response('user/privado.html', {'usuario' :usuario}, context_instance=RequestContext(request))

@login_required(login_url='/user/login')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/')