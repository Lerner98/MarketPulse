import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/')

    // Check page title
    await expect(page.locator('h2')).toContainText('Dashboard')

    // Check metrics cards are present
    await expect(page.locator('text=Total Revenue')).toBeVisible()
    await expect(page.locator('text=Total Customers')).toBeVisible()
    await expect(page.locator('text=Total Products')).toBeVisible()
    await expect(page.locator('text=Avg Order Value')).toBeVisible()
  })

  test('should display refresh button', async ({ page }) => {
    await page.goto('/')

    const refreshButton = page.locator('button', { hasText: 'Refresh Data' })
    await expect(refreshButton).toBeVisible()
  })

  test('should show chart sections', async ({ page }) => {
    await page.goto('/')

    // Check chart section titles
    await expect(page.locator('text=Revenue Trend')).toBeVisible()
    await expect(page.locator('text=Top 10 Products')).toBeVisible()
    await expect(page.locator('text=Customer Journey Flow')).toBeVisible()
  })

  test('should navigate to 404 page for invalid route', async ({ page }) => {
    await page.goto('/invalid-route')

    await expect(page.locator('h1')).toContainText('404')
    await expect(page.locator('text=Page Not Found')).toBeVisible()

    // Click on "Go to Dashboard" link
    await page.locator('text=Go to Dashboard').click()
    await expect(page).toHaveURL('/')
  })

  test('should have proper meta tags', async ({ page }) => {
    await page.goto('/')

    const title = await page.title()
    expect(title).toBe('MarketPulse - Analytics Dashboard')
  })
})
