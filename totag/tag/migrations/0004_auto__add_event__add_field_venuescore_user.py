# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Event'
        db.create_table('tag_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Venue'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Team'])),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 1, 17, 16, 36, 652383))),
        ))
        db.send_create_signal('tag', ['Event'])

        # Adding field 'VenueScore.user'
        db.add_column('tag_venuescore', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Event'
        db.delete_table('tag_event')

        # Deleting field 'VenueScore.user'
        db.delete_column('tag_venuescore', 'user_id')


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
        'tag.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Team']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 1, 17, 16, 36, 652383)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Venue']"})
        },
        'tag.team': {
            'Meta': {'object_name': 'Team'},
            'campus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Campus']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'motto': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'venues': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tag.Venue']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'tag.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'campus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Campus']", 'null': 'True', 'blank': 'True'}),
            'currentVenue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Venue']", 'null': 'True', 'blank': 'True'}),
            'currentVenueLastPing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fb_authcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fid': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
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
            'tag_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Team']", 'null': 'True', 'blank': 'True'}),
            'tag_playable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zip': ('django.db.models.fields.IntegerField', [], {})
        },
        'tag.venuescore': {
            'Meta': {'object_name': 'VenueScore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Team']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Venue']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tag']
