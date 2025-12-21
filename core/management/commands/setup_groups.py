from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Configura grupos e permissões do sistema'

    def handle(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(PerfilUsuario)
        
        perm_estudante = Permission.objects.get(
            codename='visualizar_dashboard_estudante',
            content_type=content_type
        )
        perm_professor = Permission.objects.get(
            codename='visualizar_dashboard_professor',
            content_type=content_type
        )
        perm_startup = Permission.objects.get(
            codename='visualizar_dashboard_startup',
            content_type=content_type
        )
        perm_empresa = Permission.objects.get(
            codename='visualizar_dashboard_empresa',
            content_type=content_type
        )
        perm_gerenciar = Permission.objects.get(
            codename='gerenciar_usuarios',
            content_type=content_type
        )
        
        grupo_estudantes, created = Group.objects.get_or_create(name='Estudantes')
        grupo_estudantes.permissions.set([perm_estudante])
        self.stdout.write(self.style.SUCCESS('Grupo Estudantes configurado'))
        
        grupo_professores, created = Group.objects.get_or_create(name='Professores')
        grupo_professores.permissions.set([perm_professor])
        self.stdout.write(self.style.SUCCESS('Grupo Professores configurado'))
        
        grupo_startups, created = Group.objects.get_or_create(name='Startups')
        grupo_startups.permissions.set([perm_startup])
        self.stdout.write(self.style.SUCCESS('Grupo Startups configurado'))
        
        grupo_empresas, created = Group.objects.get_or_create(name='Empresas')
        grupo_empresas.permissions.set([perm_empresa])
        self.stdout.write(self.style.SUCCESS('Grupo Empresas configurado'))
        
        grupo_admin, created = Group.objects.get_or_create(name='Administradores')
        grupo_admin.permissions.set([
            perm_estudante,
            perm_professor,
            perm_startup,
            perm_empresa,
            perm_gerenciar
        ])
        self.stdout.write(self.style.SUCCESS('Grupo Administradores configurado'))
        
        self.stdout.write(self.style.SUCCESS('Configuração concluída com sucesso!'))