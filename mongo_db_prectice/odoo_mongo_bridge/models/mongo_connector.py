# import datetime
# import logging

# from odoo import models, fields
# from odoo.exceptions import UserError
# from pymongo import MongoClient

# _logger = logging.getLogger(__name__)


# def sanitize_for_mongo(obj):
#     """Recursively convert Odoo read() data into Mongo-safe types."""
#     # Primitive safe types
#     if isinstance(obj, (int, float, str, bool)) or obj is None:
#         return obj

#     # datetime.datetime is OK for Mongo
#     if isinstance(obj, datetime.datetime):
#         return obj

#     # datetime.date -> convert to datetime at midnight
#     if isinstance(obj, datetime.date):
#         return datetime.datetime.combine(obj, datetime.time())

#     # Lists / tuples -> sanitize items
#     if isinstance(obj, (list, tuple)):
#         return [sanitize_for_mongo(x) for x in obj]

#     # Dicts -> sanitize values
#     if isinstance(obj, dict):
#         return {k: sanitize_for_mongo(v) for k, v in obj.items()}

#     # Fallback: store string representation
#     return str(obj)

# class MongoConnector(models.Model):
#     _name = "mongo.connector"
#     _description = "MongoDB Connector"

#     name = fields.Char(default="MongoDB Connection Bridge")

#     # Archiving config
#     archive_model = fields.Char(
#         string="Model Technical Name",
#         default="res.partner",  # example; can change in UI
#         help="Technical model name, e.g. 'res.partner', 'sale.order', 'account.move'.",
#     )
#     date_field_name = fields.Char(
#         string="Date Field Name",
#         default="create_date",
#         help="Date/Datetime field used for filter, e.g. 'create_date', 'invoice_date', 'date_order'.",
#     )
#     before_date = fields.Date(
#         string="Archive Records Before",
#         help="All records with date < selected date will be moved to MongoDB and deleted from PostgreSQL.",
#     )

#     # -------------------------------------------------------------------------
#     # Mongo connection helper
#     # -------------------------------------------------------------------------
#     def _get_mongo_db(self):
#         """Return MongoDB database connection."""
#         _logger.info("MongoConnector(%s): creating MongoDB client", self.id)
#         client = MongoClient("mongodb://localhost:27017")
#         db = client["odoo_custom_db"]
#         _logger.info("MongoConnector(%s): connected to MongoDB DB=%s", self.id, db.name)
#         return db

#     # -------------------------------------------------------------------------
#     # Simple test buttons
#     # -------------------------------------------------------------------------
#     def action_test_insert(self):
#         # """Insert sample data into MongoDB."""
#         # self.ensure_one()
#         # _logger.info("MongoConnector(%s): action_test_insert called", self.id)

#         # db = self._get_mongo_db()
#         # collection = db["test_collection"]

#         # record = {
#         #     "from_odoo": True,
#         #     "timestamp": datetime.datetime.utcnow(),
#         #     "message": "Hello from Odoo 19",
#         #     "user": self.env.user.name,
#         # }

#         # _logger.info("MongoConnector(%s): inserting test record into test_collection: %s", self.id, record)
#         # collection.insert_one(record)

#         # return {
#         #     "type": "ir.actions.client",
#         #     "tag": "display_notification",
#         #     "params": {
#         #         "title": "MongoDB",
#         #         "message": "Test data inserted successfully!",
#         #         "type": "success",
#         #         "sticky": False,
#         #     },
#         # }


#         # def action_restore_partners_from_mongo(self):
#         """
#         Restore partners from MongoDB collection 'res_partner_archive' back into res.partner,
#         then delete those documents from MongoDB.

#         Uses almost all fields stored in Mongo:
#         - includes all simple fields (char, text, int, float, bool, date, datetime, monetary, selection, html)
#         - includes many2one fields (if stored as id or [id, name])
#         - skips:
#             * fields starting with '_' (_id, _odoo_id, _odoo_model, ...)
#             * 'id', 'display_name', '__last_update'
#             * one2many / many2many and any value that is still a list/dict for scalar fields
#         """
#         self.ensure_one()
#         _logger.info("MongoConnector(%s): action_restore_partners_from_mongo called", self.id)

#         # Connect to Mongo
#         client = MongoClient("mongodb://localhost:27017")
#         db = client["odoo_custom_db"]
#         collection = db["res_partner_archive"]

#         docs = list(collection.find())
#         _logger.info(
#             "MongoConnector(%s): found %s document(s) in res_partner_archive to restore",
#             self.id,
#             len(docs),
#         )

#         if not docs:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "display_notification",
#                 "params": {
#                     "title": "Restore from MongoDB",
#                     "message": "No archived partners found in MongoDB.",
#                     "type": "warning",
#                     "sticky": False,
#                 },
#             }

#         Partner = self.env["res.partner"]
#         created_count = 0
#         mongo_ids_to_delete = []

#         for doc in docs:
#             vals = {}

#             for key, value in doc.items():
#                 # skip meta / technical keys
#                 if key.startswith("_"):
#                     continue
#                 if key in ("id", "display_name", "__last_update"):
#                     continue

#                 field = Partner._fields.get(key)
#                 if not field:
#                     # field does not exist on res.partner -> skip
#                     continue

#                 # skip x2many types completely
#                 if field.type in ("one2many", "many2many"):
#                     continue

#                 # sanitize value depending on field type
#                 val = value

#                 if field.type == "many2one":
#                     # many2one must be an integer ID
#                     if isinstance(val, (list, tuple)):
#                         # sometimes we may have [id, "Name"]
#                         if val and isinstance(val[0], int):
#                             val = val[0]
#                         else:
#                             # can't safely convert -> skip this field
#                             continue
#                     elif not isinstance(val, int):
#                         # name string like "Azure Interior" -> skip
#                         continue

#                 else:
#                     # non many2one scalar fields must NOT be list/dict
#                     if isinstance(val, (list, dict)):
#                         # example: ["Azure Interior", 15] or more complex things
#                         continue

#                 vals[key] = val

#             # ensure name
#             if not vals.get("name"):
#                 vals["name"] = doc.get("name") or "Restored Partner"

#             _logger.info(
#                 "MongoConnector(%s): creating res.partner with vals=%s",
#                 self.id,
#                 vals,
#             )
#             partner = Partner.create(vals)
#             created_count += 1

#             # track which Mongo docs we restored (by _id)
#             mongo_ids_to_delete.append(doc["_id"])

#         # Delete restored docs from MongoDB
#         if mongo_ids_to_delete:
#             _logger.info(
#                 "MongoConnector(%s): deleting %s restored docs from MongoDB",
#                 self.id,
#                 len(mongo_ids_to_delete),
#             )
#             collection.delete_many({"_id": {"$in": mongo_ids_to_delete}})

#         _logger.info(
#             "MongoConnector(%s): action_restore_partners_from_mongo finished: %s partner(s) restored",
#             self.id,
#             created_count,
#         )

#         return {
#             "type": "ir.actions.client",
#             "tag": "display_notification",
#             "params": {
#                 "title": "Restore Completed",
#                 "message": f"{created_count} partner(s) restored from MongoDB to PostgreSQL with all compatible fields.",
#                 "type": "success",
#                 "sticky": True,
#             },
#         }

#     def action_test_read(self):
#         """Read last 5 records from MongoDB."""
#         self.ensure_one()
#         _logger.info("MongoConnector(%s): action_test_read called", self.id)

#         db = self._get_mongo_db()
#         collection = db["test_collection"]

#         last_records = list(collection.find().sort("_id", -1).limit(5))
#         _logger.info("MongoConnector(%s): fetched %s record(s) from test_collection", self.id, len(last_records))

#         msg = "\n".join([str(r) for r in last_records]) or "No records found."

#         return {
#             "type": "ir.actions.client",
#             "tag": "display_notification",
#             "params": {
#                 "title": "MongoDB Records",
#                 "message": msg,
#                 "type": "info",
#                 "sticky": True,
#             },
#         }
    
    

#     def action_archive_all_sales(self):
#         """
#         Transfer sale.order records + their sale.order.line records
#         from PostgreSQL to MongoDB.

#         - Reads headers and lines
#         - Embeds lines under 'order_lines' in Mongo
#         - (You can then delete from Postgres via SQL if you want)
#         """
#         self.ensure_one()
#         _logger.info("MongoConnector(%s): action_archive_all_sales (with lines) called", self.id)

#         SaleOrder = self.env["sale.order"]

#         # ------------------------------------------------------------------
#         # 1) Select sale orders to transfer
#         # ------------------------------------------------------------------
#         domain = [("state", "in", ["sale", "done"])]

#         date_field_name = self.date_field_name or "create_date"
#         before_date = self.before_date
#         if before_date:
#             field = SaleOrder._fields.get(date_field_name)
#             if not field or field.type not in ("date", "datetime"):
#                 raise UserError(
#                     "Invalid date field '%s' for sale.order. "
#                     "Please configure a valid date/datetime field." % date_field_name
#                 )
#             domain.append((date_field_name, "<", before_date))

#         orders = SaleOrder.search(domain)
#         if not orders:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "display_notification",
#                 "params": {
#                     "title": "Archive Sales",
#                     "message": "No sale orders found for the given filters.",
#                     "type": "warning",
#                     "sticky": False,
#                 },
#             }

#         _logger.info(
#             "MongoConnector(%s): found %s sale.order record(s) to transfer",
#             self.id,
#             len(orders),
#         )

#         # ------------------------------------------------------------------
#         # 2) Read headers and lines
#         # ------------------------------------------------------------------
#         raw_orders = orders.read()  # list of dicts (headers)

#         # build map: order_id -> list of line dicts
#         lines_by_order = {}
#         all_lines = orders.mapped("order_line")
#         if all_lines:
#             raw_lines = all_lines.read()  # each line dict has order_id (id) field
#             for line in raw_lines:
#                 oid = line.get("order_id") and line["order_id"][0]  # [id, "Name"]
#                 if not oid:
#                     continue
#                 lines_by_order.setdefault(oid, []).append(line)

#         _logger.info(
#             "MongoConnector(%s): read %s sale.order.line record(s)",
#             self.id,
#             len(all_lines),
#         )

#         # ------------------------------------------------------------------
#         # 3) Prepare docs and insert into Mongo
#         # ------------------------------------------------------------------
#         db = self._get_mongo_db()
#         collection = db["sale_order_archive"]

#         docs = []
#         now_dt = fields.Datetime.now()

#         for rec in raw_orders:
#             oid = rec["id"]
#             full_doc = dict(rec)  # copy header fields
#             full_doc["order_lines"] = lines_by_order.get(oid, [])

#             safe = sanitize_for_mongo(full_doc)
#             safe["_odoo_model"] = "sale.order"
#             safe["_odoo_id"] = oid
#             safe["_archived_at"] = now_dt

#             docs.append(safe)

#         if docs:
#             collection.insert_many(docs)

#         inserted_count = len(docs)
#         _logger.info(
#             "MongoConnector(%s): inserted %s sale.order docs (with lines) into MongoDB",
#             self.id,
#             inserted_count,
#         )

#         # ------------------------------------------------------------------
#         # 4) OPTIONAL: Hard delete from Postgres (if you want)
#         # ------------------------------------------------------------------
#         # If you want to keep them in Postgres, comment this block.
#         order_ids = orders.ids
#         if order_ids:
#             cr = self.env.cr

#             # delete lines first
#             cr.execute(
#                 """
#                 DELETE FROM sale_order_line
#                 WHERE order_id = ANY(%s)
#                 """,
#                 [order_ids],
#             )

#             # then delete headers
#             cr.execute(
#                 """
#                 DELETE FROM sale_order
#                 WHERE id = ANY(%s)
#                 """,
#                 [order_ids],
#             )

#             _logger.info(
#                 "MongoConnector(%s): hard-deleted %s sale.order record(s) from PostgreSQL",
#                 self.id,
#                 len(order_ids),
#             )

#         return {
#             "type": "ir.actions.client",
#             "tag": "display_notification",
#             "params": {
#                 "title": "Archive Sales Completed",
#                 "message": (
#                     f"{inserted_count} sale.order record(s) + lines copied to MongoDB "
#                     f"and deleted from PostgreSQL."
#                 ),
#                 "type": "success",
#                 "sticky": True,
#             },
#         }

        


#     def action_restore_sales_from_mongo(self):
#         """
#         Restore sale.order records + sale.order.line records from MongoDB
#         collection 'sale_order_archive' back into PostgreSQL, then delete docs
#         from MongoDB.

#         - Keeps original create_date / write_date for both order and lines
#         - Skips meta keys, x2many on header
#         """
#         self.ensure_one()
#         _logger.info("MongoConnector(%s): action_restore_sales_from_mongo called", self.id)

#         client = MongoClient("mongodb://localhost:27017")
#         db = client["odoo_custom_db"]
#         collection = db["sale_order_archive"]

#         docs = list(collection.find())
#         _logger.info(
#             "MongoConnector(%s): found %s document(s) in sale_order_archive to restore",
#             self.id,
#             len(docs),
#         )

#         if not docs:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "display_notification",
#                 "params": {
#                     "title": "Restore Sales",
#                     "message": "No archived sale orders found in MongoDB.",
#                     "type": "warning",
#                     "sticky": False,
#                 },
#             }

#         SaleOrder = self.env["sale.order"]
#         SaleOrderLine = self.env["sale.order.line"]
#         created_count = 0
#         mongo_ids_to_delete = []

#         cr = self.env.cr

#         for doc in docs:
#             vals = {}

#             # extract embedded lines before header loop
#             order_lines_doc = doc.get("order_lines") or []

#             # keep original timestamps for header
#             original_create_date = doc.get("create_date")
#             original_write_date = doc.get("write_date")

#             for key, value in doc.items():
#                 # skip meta / technical keys
#                 if key.startswith("_"):
#                     continue
#                 if key in ("id", "display_name", "__last_update"):
#                     continue
#                 if key == "order_lines":
#                     # handled separately
#                     continue

#                 field = SaleOrder._fields.get(key)
#                 if not field:
#                     continue

#                 # skip x2many
#                 if field.type in ("one2many", "many2many"):
#                     continue

#                 val = value

#                 if field.type == "many2one":
#                     if isinstance(val, (list, tuple)):
#                         # [id, "Name"]
#                         if val and isinstance(val[0], int):
#                             val = val[0]
#                         else:
#                             continue
#                     elif not isinstance(val, int):
#                         continue
#                 else:
#                     if isinstance(val, (list, dict)):
#                         continue

#                 vals[key] = val

#             # partner is mandatory
#             if "partner_id" not in vals or not vals["partner_id"]:
#                 raise UserError("Cannot restore sale order without partner_id. Check archived data.")

#             _logger.info(
#                 "MongoConnector(%s): creating sale.order with vals=%s",
#                 self.id,
#                 vals,
#             )
#             order = SaleOrder.create(vals)
#             created_count += 1

#             # restore header timestamps
#             if original_create_date:
#                 cr.execute(
#                     "UPDATE sale_order SET create_date = %s WHERE id = %s",
#                     (original_create_date, order.id),
#                 )
#             if original_write_date:
#                 cr.execute(
#                     "UPDATE sale_order SET write_date = %s WHERE id = %s",
#                     (original_write_date, order.id),
#                 )

#             # ------------------------------------------------------
#             # Restore order lines
#             # ------------------------------------------------------
#             for line_doc in order_lines_doc:
#                 line_vals = {}

#                 line_create_date = line_doc.get("create_date")
#                 line_write_date = line_doc.get("write_date")

#                 for lkey, lval in line_doc.items():
#                     # skip meta / tech
#                     if lkey.startswith("_"):
#                         continue
#                     if lkey in ("id", "display_name", "__last_update"):
#                         continue
#                     if lkey == "order_id":
#                         # always set to new order.id
#                         continue

#                     lfield = SaleOrderLine._fields.get(lkey)
#                     if not lfield:
#                         continue

#                     # skip x2many on line for now (taxes, analytic tags you can add later)
#                     if lfield.type in ("one2many", "many2many"):
#                         continue

#                     val2 = lval

#                     if lfield.type == "many2one":
#                         if isinstance(val2, (list, tuple)):
#                             if val2 and isinstance(val2[0], int):
#                                 val2 = val2[0]
#                             else:
#                                 continue
#                         elif not isinstance(val2, int):
#                             continue
#                     else:
#                         if isinstance(val2, (list, dict)):
#                             continue

#                     line_vals[lkey] = val2

#                 # link line to restored order
#                 line_vals["order_id"] = order.id

#                 if not line_vals.get("product_id") and not line_vals.get("name"):
#                     # skip completely broken lines
#                     continue

#                 line = SaleOrderLine.create(line_vals)

#                 # restore line timestamps
#                 if line_create_date:
#                     cr.execute(
#                         "UPDATE sale_order_line SET create_date = %s WHERE id = %s",
#                         (line_create_date, line.id),
#                     )
#                 if line_write_date:
#                     cr.execute(
#                         "UPDATE sale_order_line SET write_date = %s WHERE id = %s",
#                         (line_write_date, line.id),
#                     )

#             # track doc to delete from Mongo
#             mongo_ids_to_delete.append(doc["_id"])

#         # delete restored docs from MongoDB
#         if mongo_ids_to_delete:
#             _logger.info(
#                 "MongoConnector(%s): deleting %s restored docs from MongoDB",
#                 self.id,
#                 len(mongo_ids_to_delete),
#             )
#             collection.delete_many({"_id": {"$in": mongo_ids_to_delete}})

#         _logger.info(
#             "MongoConnector(%s): action_restore_sales_from_mongo finished: %s sale.order record(s) restored",
#             self.id,
#             created_count,
#         )

#         return {
#             "type": "ir.actions.client",
#             "tag": "display_notification",
#             "params": {
#                 "title": "Restore Sales Completed",
#                 "message": f"{created_count} sale.order record(s) + lines restored from MongoDB to PostgreSQL with original timestamps.",
#                 "type": "success",
#                 "sticky": True,
#             },
#         }

# models/sale_order_archive.py
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId  # from `pymongo` / `bson`

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_archived = fields.Boolean(default=False)
    mongo_object_id = fields.Char()
    archived_at = fields.Datetime()

    def _mongo_safe_value(self, value):
        """Convert Odoo/Python values into MongoDB-friendly values."""
        # Convert date/datetime to ISO string
        if isinstance(value, (date, datetime)):
            return value.isoformat()

        # Recursively handle lists/tuples
        if isinstance(value, (list, tuple)):
            return [self._mongo_safe_value(v) for v in value]

        # Recursively handle dicts
        if isinstance(value, dict):
            return {k: self._mongo_safe_value(v) for k, v in value.items()}

        # Leave ObjectId as-is
        if isinstance(value, ObjectId):
            return value

        # Everything else (str, int, float, bool, None, etc.) is fine
        return value

    def _mongo_safe_dict(self, data):
        """Apply _mongo_safe_value to all values in a dict."""
        return {k: self._mongo_safe_value(v) for k, v in data.items()}
    
    @api.model
    def _get_mongo_collection(self):
        # Reuse the generic Mongo connector
        return self.env['mongo.connector']._get_collection('mongo.collection.sale_order')
    @api.model
    def cron_archive_old_orders(self, years=5, limit=1000):
        collection = self._get_mongo_collection()
        old_date = fields.Date.today() - relativedelta(years=years)

        orders = self.search([
            ('date_order', '<', old_date),
            ('is_archived', '=', False),
        ], limit=limit)

        _logger.info("Archiving %s sale orders older than %s to MongoDB...", len(orders), old_date)

        for order in orders:
            raw_data = order.read()[0]
            raw_data['_odoo_model'] = order._name
            raw_data['_odoo_id'] = order.id

            # OPTIONAL: don't set _id manually; let Mongo create it
            # If you want to set it yourself, make sure it's an ObjectId or string
            # raw_data['_id'] = ObjectId()  # or leave it out

            # 🔴 IMPORTANT: sanitize data for Mongo
            safe_data = order._mongo_safe_dict(raw_data)

            mongo_id = collection.insert_one(safe_data).inserted_id

            order.write({
                'is_archived': True,
                'mongo_object_id': str(mongo_id),
                'archived_at': fields.Datetime.now(),
            })


    def get_mongo_full_data(self):
        self.ensure_one()
        if not self.is_archived or not self.mongo_object_id:
            return {}

        collection = self._get_mongo_collection()
        doc = collection.find_one({'_id': ObjectId(self.mongo_object_id)})
        if not doc:
            return {}

        doc['_id'] = str(doc['_id'])  # stringify ObjectId
        return doc

    def action_view_archived_json(self):
        """Open a dialog showing full archived JSON from Mongo"""
        self.ensure_one()
        data = self.get_mongo_full_data()
        json_text = json.dumps(data, indent=2, default=str)

        wizard = self.env['sale.order.archive.viewer'].create({
            'order_id': self.id,
            'json_data': json_text,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Archived Sale Order (MongoDB)',
            'res_model': 'sale.order.archive.viewer',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

from odoo.exceptions import UserError
from pymongo import MongoClient


class MongoConnector(models.AbstractModel):
    _name = 'mongo.connector'
    _description = 'MongoDB Connector Helper'

    def _get_collection(self, collection_param_key):
        # Automatic defaults
        DEFAULT_MONGO_URI = "mongodb://localhost:27017"
        DEFAULT_DB = "odoo_archive"

        icp = self.env['ir.config_parameter'].sudo()

        mongo_uri = icp.get_param('mongo.uri') or DEFAULT_MONGO_URI
        mongo_db = icp.get_param('mongo.db') or DEFAULT_DB
        mongo_collection = icp.get_param(collection_param_key) or "sale_order_archive"

        client = MongoClient(mongo_uri)
        return client[mongo_db][mongo_collection]

# models/sale_order_archive_viewer.py
from odoo import fields, models

class SaleOrderArchiveViewer(models.TransientModel):
    _name = 'sale.order.archive.viewer'
    _description = 'Sale Order Archive Viewer'

    order_id = fields.Many2one('sale.order', readonly=True)
    json_data = fields.Text(readonly=True)
