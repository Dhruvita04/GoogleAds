import streamlit as st
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import webbrowser

# Load Google Ads Client
client = GoogleAdsClient.load_from_storage("google-ads.yaml")
CUSTOMER_ID = ""  # Replace with your Google Ads Account ID

st.title("Google Ads Automation Chatbot 🚀")
st.write("Enter your business details, and this bot will create a Google Ad for you!")

# User Input Form
with st.form("ad_form"):
    campaign_name = st.text_input("Campaign Name", "My Automated Campaign")
    budget = st.number_input("Daily Budget ($)", min_value=1, max_value=1000, value=5) * 1_000_000  # Convert to micros
    headline = st.text_input("Ad Headline", "Best Services Near You!")
    description = st.text_area("Ad Description", "Affordable and high-quality services.")
    submit = st.form_submit_button("Create Google Ad")

if submit:
    try:
        # Step 1: Create Campaign Budget
        budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget_obj = budget_operation.create
        budget_obj.name = "Chatbot Budget"
        budget_obj.amount_micros = int(budget)
        budget_obj.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD

        budget_response = budget_service.mutate_campaign_budgets(
            customer_id=str(CUSTOMER_ID),
            operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name

        # Step 2: Create Campaign
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = campaign_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.start_date = "20250210"
        campaign.end_date = "20251231"
        campaign.campaign_budget = budget_resource_name  # Link to budget

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=str(CUSTOMER_ID),
            operations=[campaign_operation]
        )
        campaign_id = campaign_response.results[0].resource_name

        # Step 3: Create Ad Group
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = "Chatbot Ad Group"
        ad_group.campaign = campaign_id
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = 1_000_000  # $1 CPC

        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=str(CUSTOMER_ID),
            operations=[ad_group_operation]
        )
        ad_group_id = ad_group_response.results[0].resource_name

        # Step 4: Create Ad
        ad_service = client.get_service("AdGroupAdService")
        ad_operation = client.get_type("AdGroupAdOperation")
        ad = ad_operation.create
        ad.ad_group = ad_group_id
        ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        ad.ad.expanded_text_ad.headline_part1 = headline
        ad.ad.expanded_text_ad.headline_part2 = "Get a Free Quote Today"
        ad.ad.expanded_text_ad.description = description

        ad_response = ad_service.mutate_ad_group_ads(
            customer_id=str(CUSTOMER_ID),
            operations=[ad_operation]
        )
        ad_id = ad_response.results[0].resource_name

        # Generate Direct Google Ads Link
        ads_link = f"https://ads.google.com/aw/campaigns?ocid={CUSTOMER_ID}"

        st.success("Google Ad Campaign Created Successfully! 🎉")
        st.write(f"📢 **Campaign ID:** {campaign_id}")
        st.write(f"🎯 **Ad Group ID:** {ad_group_id}")
        st.write(f"🔎 **Ad ID:** {ad_id}")
        st.markdown(f"[Click here to view your ad in Google Ads]({ads_link})", unsafe_allow_html=True)

        # Open Google Ads Link Automatically
        webbrowser.open_new_tab(ads_link)

    except GoogleAdsException as ex:
        st.error(f"Google Ads API Error: {ex}")
