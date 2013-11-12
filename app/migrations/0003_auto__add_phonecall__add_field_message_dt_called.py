# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhoneCall'
        db.create_table('app_phonecall', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Message'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Contact'])),
            ('message_url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('number_called', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('call_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('dt_queued', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('dt_called', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dt_answered', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dt_acked', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('app', ['PhoneCall'])

        # Adding field 'Message.dt_called'
        db.add_column('app_message', 'dt_called',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'PhoneCall'
        db.delete_table('app_phonecall')

        # Deleting field 'Message.dt_called'
        db.delete_column('app_message', 'dt_called')


    models = {
        'app.contact': {
            'Meta': {'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_number': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'app.delivery': {
            'Meta': {'object_name': 'Delivery'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contact']"}),
            'dt_despatched': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dt_status': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Message']"}),
            'sms_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.group': {
            'Meta': {'object_name': 'Group'},
            'contact_primary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_primary'", 'to': "orm['app.Contact']"}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['app.Contact']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'app.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'dt_acked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_called': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_delivered': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_escalated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_expired': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_received': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hdr_message_id': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_recipient': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_sender': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_subject': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'header': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipient']"}),
            'sms_body': ('django.db.models.fields.TextField', [], {})
        },
        'app.phonecall': {
            'Meta': {'object_name': 'PhoneCall'},
            'call_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contact']"}),
            'dt_acked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_answered': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_called': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_queued': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Message']"}),
            'message_url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'number_called': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'app.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'escalation_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'escalation_group'", 'null': 'True', 'to': "orm['app.Group']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'require_ack_min': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'app.reply': {
            'Meta': {'object_name': 'Reply'},
            'delivery': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Delivery']"}),
            'dt_received': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'reply_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']