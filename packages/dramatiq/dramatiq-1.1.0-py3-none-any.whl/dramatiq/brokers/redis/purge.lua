-- This file is a part of Dramatiq.
--
-- Copyright (C) 2017,2018 CLEARTYPE SRL <bogdan@cleartype.io>
--
-- Dramatiq is free software; you can redistribute it and/or modify it
-- under the terms of the GNU Lesser General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or (at
-- your option) any later version.
--
-- Dramatiq is distributed in the hope that it will be useful, but WITHOUT
-- ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
-- FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
-- License for more details.
--
-- You should have received a copy of the GNU Lesser General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.

-- purge(args=[queue_name])
-- This function drops all messages from a queue.
local queue_name = ARGV[1]
local queue_acks = queue_name .. ".acks"
local queue_messages = queue_name .. ".msgs"

redis.call("del", queue_name, queue_acks, queue_messages)
