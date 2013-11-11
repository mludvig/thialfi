# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table('app_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('sms_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('app', ['Contact'])

        # Adding model 'Group'
        db.create_table('app_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('contact_primary', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contact_primary', to=orm['app.Contact'])),
        ))
        db.send_create_signal('app', ['Group'])

        # Adding M2M table for field contacts on 'Group'
        db.create_table('app_group_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['app.group'], null=False)),
            ('contact', models.ForeignKey(orm['app.contact'], null=False))
        ))
        db.create_unique('app_group_contacts', ['group_id', 'contact_id'])

        # Adding model 'Recipient'
        db.create_table('app_recipient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Group'])),
        ))
        db.send_create_signal('app', ['Recipient'])

        # Adding model 'Message'
        db.create_table('app_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('header', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sms_body', self.gf('django.db.models.fields.TextField')()),
            ('hdr_subject', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('hdr_sender', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('hdr_recipient', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('hdr_message_id', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Recipient'])),
            ('dt_received', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('dt_delivered', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dt_acked', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dt_escalated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dt_expired', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('app', ['Message'])

        # Adding model 'Delivery'
        db.create_table('app_delivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Message'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Contact'])),
            ('sms_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('dt_despatched', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('dt_status', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('app', ['Delivery'])

        # Adding model 'Reply'
        db.create_table('app_reply', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('delivery', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['app.Delivery'])),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('reply_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('dt_received', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('app', ['Reply'])


    def backwards(self, orm):
        # Deleting model 'Contact'
        db.delete_table('app_contact')

        # Deleting model 'Group'
        db.delete_table('app_group')

        # Removing M2M table for field contacts on 'Group'
        db.delete_table('app_group_contacts')

        # Deleting model 'Recipient'
        db.delete_table('app_recipient')

        # Deleting model 'Message'
        db.delete_table('app_message')

        # Deleting model 'Delivery'
        db.delete_table('app_delivery')

        # Deleting model 'Reply'
        db.delete_table('app_reply')


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
        'app.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['app.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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