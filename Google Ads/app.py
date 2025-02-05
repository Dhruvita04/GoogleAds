import streamlit as st
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ✅ Use your Test Account ID
CUSTOMER_ID = ""

# ✅ Load Google Ads Client
client = GoogleAdsClient.load_from_storage("google-ads.yaml")

st.title("🤖 Google Ads Chatbot")
st.write("Hello! I can help you create a test campaign in your Google Ads Test Account. Let's get started! 🚀")

# ✅ Chatbot-like interaction
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.campaign_name = ""
    st.session_state.budget = 5_000_000  # Default budget in micros
    st.session_state.created = False

if st.session_state.step == 1:
    st.write("📌 What's the name of your campaign?")
    campaign_name = st.text_input("Type your campaign name:", "Test Campaign")
    if st.button("Next ➡️"):
        st.session_state.campaign_name = campaign_name
        st.session_state.step = 2
        st.experimental_rerun()

elif st.session_state.step == 2:
    st.write(f"Great! Your campaign name is **{st.session_state.campaign_name}**. Now, let's set the budget.")
    budget = st.number_input("Enter daily budget in USD:", min_value=1, max_value=1000, value=5) * 1_000_000
    if st.button("Next ➡️"):
        st.session_state.budget = int(budget)
        st.session_state.step = 3
        st.experimental_rerun()

elif st.session_state.step == 3:
    st.write(f"✅ Your campaign: **{st.session_state.campaign_name}**")
    st.write(f"💰 Daily Budget: **${st.session_state.budget / 1_000_000:.2f}**")
    if st.button("🚀 Create Campaign"):
        try:
            # ✅ Step 1: Create Campaign Budget
            budget_service = client.get_service("CampaignBudgetService")
            budget_operation = client.get_type("CampaignBudgetOperation")
            budget_obj = budget_operation.create
            budget_obj.name = "Test Budget"
            budget_obj.amount_micros = st.session_state.budget
            budget_obj.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
            
            budget_response = budget_service.mutate_campaign_budgets(
                customer_id=CUSTOMER_ID,
                operations=[budget_operation]
            )
            budget_id = budget_response.results[0].resource_name

            # ✅ Step 2: Create Campaign
            campaign_service = client.get_service("CampaignService")
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = st.session_state.campaign_name
            campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = client.enums.CampaignStatusEnum.PAUSED
            campaign.campaign_budget = budget_id
            campaign.start_date = "20250210"
            campaign.end_date = "20251231"

            campaign_response = campaign_service.mutate_campaigns(
                customer_id=CUSTOMER_ID,
                operations=[campaign_operation]
            )
            campaign_id = campaign_response.results[0].resource_name

            st.session_state.created = True
            st.session_state.campaign_id = campaign_id
            st.session_state.step = 4
            st.experimental_rerun()
        except GoogleAdsException as ex:
            st.error(f"⚠️ Google Ads API Error: {ex}")

elif st.session_state.step == 4:
    st.success("🎉 Test Campaign Created Successfully!")
    st.write(f"📢 **Campaign ID:** {st.session_state.campaign_id}")
    if st.button("🔄 Create Another Campaign"):
        st.session_state.step = 1
        st.experimental_rerun()
