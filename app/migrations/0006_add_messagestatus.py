# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MessageStatus'
        db.create_table('app_messagestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Message'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dt_status', self.gf('django.db.models.fields.DateTimeField')()),
            ('note', self.gf('django.db.models.fields.CharField')(default='', max_length=500)),
        ))
        db.send_create_signal('app', ['MessageStatus'])


    def backwards(self, orm):
        # Deleting model 'MessageStatus'
        db.delete_table('app_messagestatus')


    models = {
        'app.contact': {
            'Meta': {'ordering': "['name']", 'object_name': 'Contact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sms_number': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'app.delivery': {
            'Meta': {'object_name': 'Delivery'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contact']"}),
            'dt_despatched': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dt_status': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Message']"}),
            'sms_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'app.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
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
            'dt_received': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hdr_message_id': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_recipient': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_sender': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'hdr_subject': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'header': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Recipient']"}),
            'sms_body': ('django.db.models.fields.TextField', [], {})
        },
        'app.messagestatus': {
            'Meta': {'object_name': 'MessageStatus'},
            'dt_status': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Message']"}),
            'note': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'app.phonecall': {
            'Meta': {'ordering': "['-dt_queued']", 'object_name': 'PhoneCall'},
            'call_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Contact']"}),
            'dt_acked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_answered': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_called': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_queued': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'primary_key': 'True', 'db_index': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Message']"}),
            'number_called': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'numbers_gathered': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'text_to_say': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'})
        },
        'app.recipient': {
            'Meta': {'ordering': "['address']", 'object_name': 'Recipient'},
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
            'dt_received': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'reply_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['app']