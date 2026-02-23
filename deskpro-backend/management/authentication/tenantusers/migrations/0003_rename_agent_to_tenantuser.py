from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_agent_managers'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Agent',
            new_name='TenantUser',
        ),
        migrations.RenameField(
            model_name='tenantuser',
            old_name='is_staff',
            new_name='is_admin',
        ),
    ]
