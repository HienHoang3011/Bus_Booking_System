-- Migration: Allow guest bookings by making user_id nullable
-- Date: 2025-11-03
-- Description: Modify bookings table to allow NULL user_id for guest bookings

-- Make user_id nullable in bookings table
ALTER TABLE public.bookings
ALTER COLUMN user_id DROP NOT NULL;

-- Add comment to explain the change
COMMENT ON COLUMN public.bookings.user_id IS 'User ID - NULL for guest bookings, foreign key to users table for registered users';

-- Optional: Add index for guest bookings queries
CREATE INDEX idx_bookings_guest ON public.bookings(user_id) WHERE user_id IS NULL;

-- Display confirmation
SELECT 'Migration completed: bookings.user_id is now nullable' AS status;
