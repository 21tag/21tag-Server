# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Campus'
        db.create_table('tag_campus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('tag', ['Campus'])

        # Adding model 'Venue'
        db.create_table('tag_venue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('campus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Campus'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('crossstreet', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('zip', self.gf('django.db.models.fields.IntegerField')()),
            ('tag_playable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tag_owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('geolong', self.gf('django.db.models.fields.FloatField')()),
            ('geolat', self.gf('django.db.models.fields.FloatField')()),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('tag', ['Venue'])

        # Adding model 'Team'
        db.create_table('tag_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('campus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Campus'], null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('tag', ['Team'])

        # Adding M2M table for field venues on 'Team'
        db.create_table('tag_team_venues', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['tag.team'], null=False)),
            ('venue', models.ForeignKey(orm['tag.venue'], null=False))
        ))
        db.create_unique('tag_team_venues', ['team_id', 'venue_id'])

        # Adding model 'UserProfile'
        db.create_table('tag_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('campus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Campus'], null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('phone', self.gf('django.db.models.fields.IntegerField')(max_length=11, null=True, blank=True)),
            ('fid', self.gf('django.db.models.fields.IntegerField')(max_length=255, null=True, blank=True)),
            ('fb_authcode', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Team'], null=True, blank=True)),
            ('points', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('currentVenueId', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('currentVenueName', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('currentVenueTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('currentVenueLastTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('tag', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'Campus'
        db.delete_table('tag_campus')

        # Deleting model 'Venue'
        db.delete_table('tag_venue')

        # Deleting model 'Team'
        db.delete_table('tag_team')

        # Removing M2M table for field venues on 'Team'
        db.delete_table('tag_team_venues')

        # Deleting model 'UserProfile'
        db.delete_table('tag_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tag.campus': {
            'Meta': {'object_name': 'Campus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tag.team': {
            'Meta': {'object_name': 'Team'},
            'campus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Campus']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'venues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tag.Venue']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'tag.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'campus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Campus']", 'null': 'True', 'blank': 'True'}),
            'currentVenueId': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'currentVenueLastTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'currentVenueName': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'currentVenueTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fb_authcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fid': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Team']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'tag.venue': {
            'Meta': {'object_name': 'Venue'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'campus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Campus']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'crossstreet': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geolat': ('django.db.models.fields.FloatField', [], {}),
            'geolong': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'tag_playable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zip': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['tag']
