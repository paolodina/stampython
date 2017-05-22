#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing quote commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
import time

import stampy.stampy
import stampy.plugin.config
from stampy.i18n import translate
_ = translate.ugettext


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/quote"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower()[0:6] == "/quote":
            quotecommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `/quote add <id> <text>` to add a quote for that username\n")
    commandtext += _("Use `/quote <id>` to get a random quote from that username\n\n")
    if stampy.stampy.is_owner_or_admin(message):
        commandtext += _("Use `/quote del <quoteid>` to remove a quote\n\n")
    return commandtext


def quotecommands(message):
    """
    Searches for commands related to quotes
    :param message: message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /quote
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    for case in stampy.stampy.Switch(command):
        # cur.execute('CREATE TABLE quote(id AUTOINCREMENT, name TEXT,
        # date TEXT, text TEXT;')
        if case('add'):
            who_quote = texto.split(' ')[2]
            date = time.time()
            quote = str.join(" ", texto.split(' ')[3:])
            result = addquote(username=who_quote, date=date, text=quote, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            text = _("Quote `%s` added") % result
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            break
        if case('del'):
            if stampy.stampy.is_owner_or_admin(message):
                id_todel = texto.split(' ')[2]
                text = _("Deleting quote id `%s`") % id_todel
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                deletequote(id=id_todel, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            break
        if case():
            # We're just given the nick (or not), so find quote for it
            try:
                nick = texto.split(' ')[1]
            except:
                nick = False
            try:
                (quoteid, username, date, quote) = getquote(username=nick, gid=stampy.stampy.geteffectivegid(gid=chat_id))
                datefor = datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')
                text = '`%s` -- `@%s`, %s (id %s)' % (
                       quote, username, datefor, quoteid)
            except:
                if nick:
                    text = _("No quote recorded for `%s`") % nick
                else:
                    text = _("No quote found")
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")

    return


def getquote(username=False, gid=0):
    """
    Gets quote for a specified username or a random one
    :param gid: group id to filter
    :param username: username to get quote for
    :return: text for the quote or empty
    """

    logger = logging.getLogger(__name__)
    if username:
        string = (username, gid)
        sql = "SELECT id,username,date,text FROM quote WHERE username='%s' and gid='%s' ORDER BY RANDOM() LIMIT 1;" % string
    else:
        sql = "SELECT id,username,date,text FROM quote WHERE gid='%s' ORDER BY RANDOM() LIMIT 1;" % gid
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()
    logger.debug(msg="getquote: %s for gid: %s" % (username, gid))
    try:
        # Get value from SQL query
        (quoteid, username, date, quote) = value

    except:
        # Value didn't exist before, return 0
        quoteid = False
        username = False
        date = False
        quote = False

    if quoteid:
        return quoteid, username, date, quote

    return False


def addquote(username=False, date=False, text=False, gid=0):
    """
    Adds a quote for a specified username
    :param gid: group id to filter
    :param username: username to store quote for
    :param date: date when quote was added
    :param text: text of the quote
    :return: returns quote ID entry in database
    """

    logger = logging.getLogger(__name__)
    sql = "INSERT INTO quote(username, date, text, gid) VALUES('%s','%s', '%s', '%s');" % (
          username, date, text, gid)
    cur = stampy.stampy.dbsql(sql)
    logger.debug(msg=_("createquote: %s=%s on %s for group %s") % (username, text, date, gid))
    # Retrieve last id
    sql = "select last_insert_rowid();"
    cur = stampy.stampy.dbsql(sql)
    lastrowid = cur.fetchone()[0]
    return lastrowid


def deletequote(id=False, gid=0):
    """
    Deletes quote from the database
    :param gid: group id to filter
    :param id: ID of the quote to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM quote WHERE id='%s' AND gid='%s';" % (id, gid)
    logger.debug(msg="deletequote: %s, group: %s" % (id, gid))
    return stampy.stampy.dbsql(sql)
