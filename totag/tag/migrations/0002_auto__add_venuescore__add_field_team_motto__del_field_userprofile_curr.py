# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'VenueScore'
        db.create_table('tag_venuescore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Team'], null=True, blank=True)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Venue'], null=True, blank=True)),
        ))
        db.send_create_signal('tag', ['VenueScore'])

        # Adding field 'Team.motto'
        db.add_column('tag_team', 'motto', self.gf('django.db.models.fields.CharField')(default='Mottos Rule', max_length=255), keep_default=False)

        # Deleting field 'UserProfile.currentVenueLastTime'
        db.delete_column('tag_userprofile', 'currentVenueLastTime')

        # Deleting field 'UserProfile.currentVenueName'
        db.delete_column('tag_userprofile', 'currentVenueName')

        # Deleting field 'UserProfile.currentVenueTime'
        db.delete_column('tag_userprofile', 'currentVenueTime')

        # Deleting field 'UserProfile.currentVenueId'
        db.delete_column('tag_userprofile', 'currentVenueId')

        # Adding field 'UserProfile.currentVenue'
        db.add_column('tag_userprofile', 'currentVenue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Venue'], null=True, blank=True), keep_default=False)

        # Adding field 'UserProfile.currentVenueLastPing'
        db.add_column('tag_userprofile', 'currentVenueLastPing', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'VenueScore'
        db.delete_table('tag_venuescore')

        # Deleting field 'Team.motto'
        db.delete_column('tag_team', 'motto')

        # Adding field 'UserProfile.currentVenueLastTime'
        db.add_column('tag_userprofile', 'currentVenueLastTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'UserProfile.currentVenueName'
        db.add_column('tag_userprofile', 'currentVenueName', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'UserProfile.currentVenueTime'
        db.add_column('tag_userprofile', 'currentVenueTime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'UserProfile.currentVenueId'
        db.add_column('tag_userprofile', 'currentVenueId', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'UserProfile.currentVenue'
        db.delete_column('tag_userprofile', 'currentVenue_id')

        # Deleting field 'UserProfile.currentVenueLastPing'
        db.delete_column('tag_userprofile', 'currentVenueLastPing')


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
        },
        'tag.venuescore': {
            'Meta': {'object_name': 'VenueScore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Team']", 'null': 'True', 'blank': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Venue']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tag']
